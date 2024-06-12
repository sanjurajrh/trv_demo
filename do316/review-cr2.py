#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Web Apr 27 2022 Herve Quatremain <hquatrem@redhat.com>
#   - original code

"""
Grading module for DO316 review-cr2 lab.
This module either does start, grade, or finish for the review-cr2 lab.
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
NAMESPACE = "review-cr2"


# Disable certificate validation
disable_warnings(InsecureRequestWarning)


class ReviewCR2(OpenShift):
    """
    Comprehensive review 2 script for DO316
    """

    __LAB__ = "review-cr2"

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
                "label": f"Creating the {NAMESPACE} project",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/start_projects.yml",
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
                "label": "The dev-web-rhel8 virtual machine template exists",
                "task": self._grade_template,
                "name": "dev-web-rhel8",
                "provider": "Red Hat Training",
                "os": "rhel8",
                "disk": "http://utility.lab.example.com:8080/openshift4/images/helloworld.qcow2",
                "flavor": "tiny",
                "workload": "server",
                "dv_name": "${NAME}",
                "disk_size": "10Gi",
                "interface": "virtio",
                "storage_class": "ocs-external-storagecluster-ceph-rbd-virtualization",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The developer user has admin rights",
                "task": self._grade_rights,
                "name": "developer",
                "right": "admin",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web1 VM is running",
                "task": self._grade_vm_running,
                "name": "web1",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web1 VM was created from the template",
                "task": self._grade_vm_template,
                "name": "web1",
                "template": "dev-web-rhel8",
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
            # {
            #     "label": "Deleting the NodeMaintenance resources",
            #     "task": self._delete_ge_node_maintenance,
            #     "fatal": False,
            # },
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

    def _grade_template(self, item):
        item["failed"] = False
        item["msgs"] = []
        template_name = item["name"]
        template_provider = item["provider"]
        template_os = item["os"]
        template_disk = item["disk"]
        template_flavor = item["flavor"]
        template_workload = item["workload"]
        template_disk_size = item["disk_size"]
        template_dv_name = item["dv_name"]
        # template_interface = item["interface"]
        template_storage_class = item["storage_class"]

        resource = self.resource_get(
            "template.openshift.io/v1", "Template", template_name, NAMESPACE
        )
        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {template_name} template does not exist in the {NAMESPACE} project."
                }
            ]
            return

        # Template provider
        provider = resource.metadata.annotations.get("template.kubevirt.io/provider")
        if provider is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The template provider, {template_provider}, is not set."}
            )
        elif provider.lower() != template_provider.lower():
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"Wrong template provider type: got '{provider}' instead of '{template_provider}'."
                }
            )

        # Retrieve the VM definition
        for obj in resource.objects:
            if obj.kind == "VirtualMachine":
                vm = obj
                break
        else:
            item["failed"] = True
            item["msgs"].append({"text": "Cannot find the VM definition."})
            return

        # Operating system
        os = vm.spec.template.metadata.annotations.get("vm.kubevirt.io/os")
        if os is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The operating system, {template_os}, is not set."}
            )
        elif os.lower() != template_os.lower():
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"Wrong operating system: got '{os}' instead of '{template_os}'."
                }
            )

        # Flavor
        flavor = vm.spec.template.metadata.annotations.get("vm.kubevirt.io/flavor")
        if flavor is None:
            item["failed"] = True
            item["msgs"].append({"text": f"The flavor, {template_flavor}, is not set."})
        elif flavor.lower() != template_flavor.lower():
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"Wrong flavor: got '{flavor}' instead of '{template_flavor}'."
                }
            )

        # Workload type
        workload = vm.spec.template.metadata.annotations.get("vm.kubevirt.io/workload")
        if workload is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The workload type, {template_workload}, is not set."}
            )
        elif workload.lower() != template_workload.lower():
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"Wrong workload type: got '{workload}' instead of '{template_workload}'."
                }
            )

        # Retrieve the disk definition
        try:
            dv = vm.spec.dataVolumeTemplates[0]
        except Exception:
            item["failed"] = True
            item["msgs"].append({"text": "Cannot find the disk definition."})
            return

        # Retrieve the disk name
        try:
            dv_name = dv.metadata.name
        except Exception:
            item["failed"] = True
            item["msgs"].append({"text": "The datavolume name is not set"})
        else:
            if dv_name.lower() != template_dv_name.lower():
                item["failed"] = True
                item["msgs"].append(
                    {
                        "text": f"Wrong datavolume name: got '{dv_name}' installed of '{template_dv_name}'"
                    }
                )

        # Disk URL
        try:
            disk = dv.spec.source.http.url
        except Exception:
            item["failed"] = True
            item["msgs"].append({"text": "The disk URL is not set."})
        else:
            if disk.lower() != template_disk.lower():
                item["failed"] = True
                item["msgs"].append(
                    {
                        "text": f"Wrong disk URL: got '{disk}' instead of '{template_disk}'."
                    }
                )

        # Disk size
        try:
            disk_size = dv.spec.storage.resources.requests.storage
        except Exception:
            item["failed"] = True
            item["msgs"].append({"text": "The disk size is not set."})
        else:
            if disk_size.lower() != template_disk_size.lower():
                item["failed"] = True
                item["msgs"].append(
                    {
                        "text": f"Wrong disk size: got '{disk_size}' instead of '{template_disk_size}'."
                    }
                )

        # Storage class
        try:
            storage_class = dv.spec.storage.storageClassName
        except Exception:
            item["failed"] = True
            item["msgs"].append({"text": "The disk storage class is not set."})
        else:
            if storage_class.lower() != template_storage_class.lower():
                item["failed"] = True
                item["msgs"].append(
                    {
                        "text": f"Wrong disk storage class: got '{storage_class}' instead of '{template_storage_class}'."
                    }
                )

    def _grade_rights(self, item):
        item["failed"] = False
        user_name = item["name"]
        user_right = item["right"]

        resources = self.oc_client.resources.get(
            api_version="rbac.authorization.k8s.io/v1", kind="RoleBinding"
        )
        rbs = resources.get(namespace=NAMESPACE)
        for rb in rbs.items:
            try:
                if rb.roleRef.name == user_right and rb.subjects[0].name == user_name:
                    return
            except Exception:
                pass

        item["failed"] = True
        item["msgs"] = [
            {
                "text": f"Cannot find the {user_right} right for the {user_name} user in the {NAMESPACE} project."
            }
        ]

    def _grade_vm_template(self, item):
        item["failed"] = False
        vm_name = item["name"]
        template = item["template"]

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        )

        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]
            return

        templ = resource.metadata.labels.get("vm.kubevirt.io/template")
        if templ is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {vm_name} VM was not created from the {template} template."
                }
            ]
            return

        if templ.lower() != template.lower():
            item["failed"] = True
            item["msgs"] = [
                {"text": f"Wrong template: got '{templ}' instead of '{template}'."}
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
