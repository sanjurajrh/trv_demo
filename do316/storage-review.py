#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Mar 21 2022 Herve Quatremain <hquatrem@redhat.com>
#   original code
# * Mar 27 2024 Andres Hernandez <andres.hernandez@redhat.com>
#   Version bump to OCP 4.14

"""
Grading module for DO316 storage-review lab.
This module either does start, grade, or finish for the storage-review lab.
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
NAMESPACE = "storage-review"


# Disable certificate validation
disable_warnings(InsecureRequestWarning)


class StorageReview(OpenShift):
    """
    Storage Review lab script for DO316
    """

    __LAB__ = "storage-review"

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
                "label": f"Confirming that the {NAMESPACE} project does not exist",
                "task": self._check_ge_namespace,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Preparing external storage",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/start_image_and_nfs.yml",
                "fatal": True,
            },
            {
                "label": "Creating the vm1 virtual machine",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/vm1.yml",
                "fatal": True,
            },
            {
                "label": "Creating the vm2 virtual machine",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/vm2.yml",
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
                "label": "The vm1 VM is running",
                "task": self._grade_vm_running,
                "name": "vm1",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The vm2 VM is running",
                "task": self._grade_vm_running,
                "name": "vm2",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The webroot disk is not connected to vm1",
                "task": self._grade_vm_no_disk,
                "name": "vm1",
                "disk_name": "webroot",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The webroot disk is connected to vm2",
                "task": self._grade_vm_pvc,
                "name": "vm2",
                "pvc_name": "webroot",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The PV named nfs-pv is reserved",
                "task": self._grade_pv,
                "name": "nfs-pv",
                "claimref_pvc": "weblog",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The weblog PVC exists",
                "task": self._grade_pvc,
                "name": "weblog",
                "pv_name": "nfs-pv",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The weblog PVC is connected to vm2",
                "task": self._grade_vm_pvc,
                "name": "vm2",
                "pvc_name": "weblog",
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
                "label": f"Deleting the {NAMESPACE} project",
                "task": self._delete_ge_namespace,
                "fatal": True,
            },
            {
                "label": "Deleting the NFS persistent volume",
                "task": self._delete_ge_pv,
                "fatal": True,
            },
            {
                "label": "Removing the external storage",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/finish_image_and_nfs.yml",
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

    def _delete_ge_pv(self, item):
        item["failed"] = False
        try:
            self.delete_resource("v1", "PersistentVolume", "nfs-pv", "")
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [{"text": "Failed removing the 'nfs-pv' PV: %s" % e}]

    def _grade_vm_running(self, item):
        item["failed"] = False
        vmi_name = item["name"]

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachineInstance", vmi_name, NAMESPACE
        )

        try:
            status = resource.status.phase
        except Exception:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {vmi_name} VM is not running."}]
            return

        if status.lower() != "running":
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vmi_name} VM is not running: current status: {status}"}
            ]

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
            volume_name = v.get("name", "").lower()
            if volume_name == disk_name:
                item["failed"] = True
                item["msgs"] = [
                    {"text": f"The {disk_name} disk is still attached to the VM."}
                ]
                return

    def _grade_vm_pvc(self, item):
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
                pvc = v.persistentVolumeClaim.claimName.lower()
            except Exception:
                continue
            if pvc == pvc_name:
                break
        else:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {pvc_name} PVC is not attached to the VM."}]

    def _grade_pv(self, item):
        item["failed"] = False
        pv_name = item["name"]
        pvc_reserved = item["claimref_pvc"].lower()

        resource = self.resource_get("v1", "PersistentVolume", pv_name, "")

        if resource is None:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {pv_name} PV does not exist."}]
            return

        try:
            claim_ref = resource.spec.claimRef
        except Exception:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {pv_name} PV is not reserved for a PVC."}]
            return

        pvc = claim_ref.get("name", "").lower()
        namespace = claim_ref.get("namespace")

        if pvc != pvc_reserved:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The PV is not reserved for the {pvc_reserved} PVC: got {pvc}"
                }
            ]
            return

        if namespace != NAMESPACE:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The PV is not reserved for the {pvc_reserved} PVC in the {NAMESPACE} namespace: got {namespace} for the namespace."
                }
            ]
            return

    def _grade_pvc(self, item):
        item["failed"] = False
        item["msgs"] = []
        pvc_name = item["name"]
        pv_name = item["pv_name"].lower()

        resource = self.resource_get("v1", "PersistentVolumeClaim", pvc_name, NAMESPACE)

        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {pvc_name} PVC does not exist in the {NAMESPACE} project."
                }
            ]
            return

        v = resource.spec.get("volumeName")
        if v is None:
            item["failed"] = True
            item["msgs"].append({"text": "The PVC is not bound to a PV."})
        elif v.lower() != pv_name:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The PVC is not bound to the {pv_name} PV: got {v} instead."}
            )

        v = resource.status.get("phase")
        if v is None:
            item["failed"] = True
            item["msgs"].append({"text": "The PVC is not in the Bound state."})
        elif v.lower() != "bound":
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The PVC is not in the Bound state: current state: {v}."}
            )

        v = resource.spec.get("volumeMode", "Filesystem")
        if v.lower() != "filesystem":
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The volume mode is not Filesystem: got {v} instead."}
            )

        modes = resource.spec.get("accessModes", [])
        for access_mode in modes:
            if access_mode.lower() == "readwritemany":
                break
        else:
            item["failed"] = True
            msg = ": got " + ", ".join(modes) + " instead." if len(modes) else ""
            item["msgs"].append(
                {"text": f"The access mode is not ReadWriteMany (RWX){msg}"}
            )

        try:
            v = resource.spec.resources.requests.get("storage", "0Gi")
        except Exception:
            v = "0Gi"
        if "5" not in v:
            item["failed"] = True
            msg = ": got " + ", ".join(modes) + " instead." if len(modes) else ""
            item["msgs"].append(
                {"text": f"The request size is not 5 GiB: got {v} instead."}
            )
