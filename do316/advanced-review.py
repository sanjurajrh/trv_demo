#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Wed Apr 13 2022 Herve Quatremain <hquatrem@redhat.com>
#   - original code

"""
Grading module for DO316 advanced-review lab.
This module either does start, grade, or finish for the advanced-review lab.
"""

import os
import sys
import time
import logging
import requests

from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from kubernetes.client.exceptions import ApiException

from ocp import api
from ocp.utils import OpenShift
from labs import labconfig
from labs.common import labtools, userinterface

# Import all the functions defined in the common.py module
from do316 import common


# Course SKU
SKU = labconfig.get_course_sku().upper()

# List of hosts involved in that module. Before doing anything,
# the module checks that they can be reached on the network
_targets = ["utility"]

# Default namespace for the resources
NAMESPACE = "advanced-review"


# Disable certificate validation
disable_warnings(InsecureRequestWarning)


class AdvancedReview(OpenShift):
    """
    Advanced Review lab script for DO316
    """

    __LAB__ = "advanced-review"

    # Get the OCP host and port from environment variables
    OCP_API = {
        "user": os.environ.get("OCP_USER", "admin"),
        "password": os.environ.get("OCP_PASSWORD", "redhatocp"),
        "host": os.environ.get("OCP_HOST", "api.ocp4.example.com"),
        "port": os.environ.get("OCP_PORT", "6443"),
    }

    # Initialize class
    def __init__(self):
        logging.debug("{} / {}".format(SKU, sys._getframe().f_code.co_name))
        try:
            super().__init__()
        except requests.exceptions.ConnectionError:
            print(
                "The Lab environment is not ready, please wait 10 minutes before trying again."
            )
            sys.exit(1)
        except ApiException:
            print(
                "The OpenShift cluster is not ready, please wait 5 minutes before trying again."
            )
            sys.exit(1)
        except Exception as e:
            print("An unknown error ocurred: " + str(e))
            logging.exception("An unknown error ocurred: " + str(e))
            sys.exit(1)

    def start(self):
        """
        Prepare the system for starting the lab
        """
        logging.debug("{} / {}".format(SKU, sys._getframe().f_code.co_name))
        items = [
            {
                "label": "Checking lab systems",
                "task": labtools.check_host_reachable,
                "hosts": _targets,
                "fatal": True,
            },
            {
                "label": "Pinging API",
                "task": self._start_ping_api,
                "host": self.OCP_API["host"],
                "fatal": True,
            },
            {
                "label": "Checking API",
                "task": self._start_check_api,
                "host": self.OCP_API["host"],
                "port": self.OCP_API["port"],
                "fatal": True,
            },
            {
                "label": "Checking cluster readiness",
                "task": self._start_check_cluster_ready,
                "fatal": True,
            },
            {
                "label": "Verifying OpenShift Virtualization Operator",
                "task": common.openshift_virt,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Verifying Node Maintenance Operator",
                "task": common.node_maintenance,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Verifying storage class defaults",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/revert-cluster.yml",
                "fatal": True,
            },
            {
                "label": f"Confirming that the {NAMESPACE} project does not exist",
                "task": self._check_ge_namespace,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Creating the golden-rhel virtual machine",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/golden.yml",
                "fatal": True,
            },
            {
                "label": "Copying exercise content",
                "task": labtools.copy_lab_files,
                "lab_name": self.__LAB__,
                "fatal": True,
            },
            {
                "label": "Confirming virtctl availability",
                "task": self.run_playbook,
                "playbook": "ansible/roles/deploy-virtctl.yml",
                "fatal": True,
            },
        ]
        userinterface.Console(items).run_items(action="Starting")

    def grade(self):
        """
        Perform evaluation steps on the system
        """
        logging.debug("{} / {}".format(SKU, sys._getframe().f_code.co_name))
        items = [
            {
                "label": "Checking lab systems",
                "task": labtools.check_host_reachable,
                "hosts": _targets,
                "fatal": True,
            },
            {
                "label": "The golden-rhel VM exists",
                "task": self._grade_vm_exists,
                "name": "golden-rhel",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The www1 VM exists",
                "task": self._grade_vm_exists,
                "name": "www1",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The golden-snap1 snapshot exists",
                "task": self._grade_vm_snapshot_exists,
                "name": "golden-snap1",
                "vm_name": "golden-rhel",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The root-copy PVC exists",
                "task": self._grade_pvc,
                "name": "root-copy",
                "class_name": "ocs-external-storagecluster-ceph-rbd-virtualization",
                "mode_name": "ReadWriteMany",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The www2 VM exists",
                "task": self._grade_vm_disk,
                "name": "www2",
                "pvc_name": "root-copy",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The misconfigured disk is not connected to golden-rhel",
                "task": self._grade_vm_no_disk,
                "name": "golden-rhel",
                "disk_name": "tempdata",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirming that the NodeMaintenance resource exists",
                "task": self._grade_nm_exists,
                "name": "node-maintenance",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The worker02 node is cordoned off and drained",
                "task": self._grade_node_cordon,
                "name": "worker02",
                "fatal": False,
                "grading": True,
            },
        ]
        ui = userinterface.Console(items)
        ui.run_items(action="Grading")
        ui.report_grade()

    def finish(self):
        """
        Perform post-lab cleanup
        """
        logging.debug("{} / {}".format(SKU, sys._getframe().f_code.co_name))
        items = [
            {
                "label": "Checking lab systems",
                "task": labtools.check_host_reachable,
                "hosts": _targets,
                "fatal": True,
            },
            {
                "label": "Deleting the NodeMaintenance resources",
                "task": self._delete_ge_node_maintenance,
                "fatal": True,
            },
            {
                "label": "Uncordoning the nodes",
                "task": self._delete_ge_uncordon,
                "fatal": True,
            },
            {
                "label": f"Deleting the {NAMESPACE} project (be patient)",
                "task": self._delete_ge_namespace,
                "fatal": True,
            },
            {
                "label": "Deleting exercise files",
                "task": labtools.delete_workdir,
                "lab_name": self.__LAB__,
                "fatal": True,
            },
        ]
        userinterface.Console(items).run_items(action="Finishing")

    def _start_ping_api(self, item):
        """
        Execute a task to prepare the system for the lab
        """
        if item["host"] is None:
            item["failed"] = True
            item["msgs"] = [{"text": "OCP_HOST is not defined"}]
        else:
            check = labtools.ping(item["host"])
            for key in check:
                item[key] = check[key]

    def _start_check_api(self, item):
        if item["host"] is None or item["port"] is None:
            item["failed"] = True
            item["msgs"] = [{"text": "OCP_HOST and OCP_PORT are not defined"}]
        else:
            if api.isApiUp(item["host"], port=item["port"]):
                item["failed"] = False
            else:
                item["failed"] = True
                item["msgs"] = [
                    {
                        "text": "API could not be reached: https://{}:{}/".format(
                            item["host"], item["port"]
                        )
                    }
                ]

    def _start_check_cluster_ready(self, item):
        item["failed"] = True
        # Get resources from cluster to check API
        self.oc_client.resources.get(
            api_version="project.openshift.io/v1", kind="Project"
        ).get()
        self.oc_client.resources.get(api_version="v1", kind="Node").get()
        self.oc_client.resources.get(api_version="v1", kind="Namespace").get()

        try:
            v1_config = self.oc_client.resources.get(
                api_version="config.openshift.io/v1", kind="ClusterVersion"
            )
            cluster_version = v1_config.get().items[0]
            if cluster_version.spec.clusterID is None:
                item["failed"] = True
                item["msgs"] = [{"text": "Cluster ID could not be found"}]
            else:
                item["failed"] = False
        except Exception:
            item["msgs"] = [{"text": "Cluster is not OpenShift"}]

    def _check_ge_namespace(self, item):
        """
        Check GE namespace
        """
        item["failed"] = False
        if self.resource_exists("v1", "Namespace", (NAMESPACE), ""):
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {NAMESPACE} namespace already exists, please delete it or run 'lab finish {self.__LAB__}' before starting the exercise"
                }
            ]
        return item["failed"]

    def _delete_ge_namespace(self, item):
        item["failed"] = False
        try:
            self.delete_resource("v1", "Namespace", (NAMESPACE), "")
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {"text": "Failed removing namespace %s: %s" % (NAMESPACE, e)}
            ]
        if not item["failed"]:
            # Give time for the namespace to terminate
            time.sleep(180)

    def _delete_ge_node_maintenance(self, item):
        item["failed"] = False
        try:
            # Delete all the NodeMaintenance resources.
            # The delete() method requires name|label_selector|field_selector
            self.oc_client.resources.get(
                api_version="nodemaintenance.medik8s.io/v1beta1", kind="NodeMaintenance"
            ).delete(field_selector="metadata.name!=foobar0451")
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {"text": "Failed removing the NodeMaintenance resources: %s" % e}
            ]

    def _delete_ge_uncordon(self, item):
        item["failed"] = False
        for node in ("worker01", "worker02"):
            try:
                body = {
                    "kind": "Node",
                    "apiVersion": "v1",
                    "metadata": {"name": node},
                    "spec": None,
                }
                self.oc_client.resources.get(api_version="v1", kind="Node").patch(
                    body=body
                )
            except Exception as e:
                item["failed"] = True
                item["msgs"] = [{"text": "Failed to uncordon node %s: %s" % (node, e)}]

    def _grade_vm_exists(self, item):
        item["failed"] = False
        vm_name = item["name"]

        if not self.resource_exists(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        ):
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]

    def _grade_vm_snapshot_exists(self, item):
        item["failed"] = False
        snap_name = item["name"]
        vm_name = item["vm_name"]

        resource = self.resource_get(
            "snapshot.kubevirt.io/v1alpha1",
            "VirtualMachineSnapshot",
            snap_name,
            NAMESPACE,
        )

        try:
            vm = resource.spec.source.name
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {snap_name} snapshot does not exist in the {NAMESPACE} project."
                }
            ]
            return

        if vm != vm_name:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {snap_name} snapshot is not a snapshot of the {vm_name} VM: it is a snapshot of {vm}."
                }
            ]

    def _grade_pvc(self, item):
        item["failed"] = False
        item["msgs"] = []
        pvc_name = item["name"]
        class_name = item["class_name"].lower()
        mode_name = item["mode_name"]

        resource = self.resource_get("v1", "PersistentVolumeClaim", pvc_name, NAMESPACE)

        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {pvc_name} PVC does not exist in the {NAMESPACE} project."
                }
            ]
            return

        pvc_class = resource.spec.get("storageClassName")
        if pvc_class is None:
            item["failed"] = True
            item["msgs"].append({"text": f"The PVC storage class is not {class_name}."})
        elif pvc_class.lower() != class_name:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"The PVC storage class is not {class_name}: got {pvc_class} instead."
                }
            )

        modes = resource.spec.get("accessModes", [])
        for access_mode in modes:
            if access_mode.lower() == mode_name.lower():
                break
        else:
            item["failed"] = True
            msg = ": got " + ", ".join(modes) + " instead." if len(modes) else ""
            item["msgs"].append({"text": f"The access mode is not {mode_name}{msg}"})

    def _grade_vm_disk(self, item):
        item["failed"] = False
        vm_name = item["name"]
        pvc_name = item["pvc_name"].lower()

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        )

        try:
            volumes = resource.spec.template.spec.volumes
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]
            return

        for v in volumes:
            try:
                claim_name = v.persistentVolumeClaim.claimName.lower()
                if claim_name == pvc_name:
                    break
            except Exception:
                pass
        else:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {pvc_name} PVC is not attached to the VM."}]

    def _grade_vm_no_disk(self, item):
        item["failed"] = False
        vm_name = item["name"]
        disk_name = item["disk_name"].lower()

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        )

        try:
            volumes = resource.spec.template.spec.volumes
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]
            return

        for v in volumes:
            if v.get("name", "").lower() == disk_name:
                item["failed"] = True
                item["msgs"] = [
                    {"text": f"The {disk_name} disk is still attached to the VM."}
                ]
                return

    def _grade_node_cordon(self, item):
        item["failed"] = False
        item["msgs"] = []
        node_name = item["name"]

        resource = self.resource_get("v1", "Node", node_name, "")

        if resource is None:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {node_name} node does not exist."}]
            return

        sched = resource.spec.get("unschedulable")
        if sched is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"Workload can still be scheduled on {node_name}."}
            )

        try:
            resource = self.oc_client.resources.get(
                api_version="kubevirt.io/v1", kind="VirtualMachineInstance"
            )
            vmi_list = resource.get(namespace=NAMESPACE)
            for vmi in vmi_list.items:
                node = vmi.status.get("nodeName")
                if node is not None and node == node_name:
                    vm_name = vmi.metadata.name
                    item["failed"] = True
                    item["msgs"].append(
                        {
                            "text": f"Node not drained: the {vm_name} VM is still running on {node_name}."
                        }
                    )
        except Exception:
            pass

    def _grade_nm_exists(self, item):
        item["failed"] = False
        nm_name = item["name"]

        if not self.resource_exists(
            "nodemaintenance.medik8s.io/v1beta1", "NodeMaintenance", nm_name, NAMESPACE
        ):
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {nm_name} NodeMaintenance does not exist in the {NAMESPACE} project."
                }
            ]
