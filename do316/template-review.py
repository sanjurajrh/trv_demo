#
# Copyright (c) 2021 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Apr 25 2022 Natalie Lind <nlind@redhat.com>
#   - original code

"""
Grading module for DO316 template-create guided exercise.
This module either does start, grading, or finish for the template-create guided exercise.
"""

import os
import sys
import logging
import requests
import time

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
_targets = [
    "utility",
]

# Default namespace for the resources
NAMESPACE = "template-review"

# Disable certificate validation
disable_warnings(InsecureRequestWarning)


# Change the class name to match your file name with WordCaps
class TemplateReview(OpenShift):
    """
    Template Review lab script for DO316
    """

    __LAB__ = "template-review"

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
                "label": "Creating exercise resources",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/resources.yml",
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
                "label": "Confirming that the mariadb-server template exists",
                "task": self._grade_template_exists,
                "name": "mariadb-server",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Checking the defined boot source and size in the mariadb-server template",
                "task": self._grade_boot_source,
                "name": "mariadb-server",
                "size": "20Gi",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirming that the web-server template exists",
                "task": self._grade_template_exists,
                "name": "web-server",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Checking the defined boot source and size in the web-server template",
                "task": self._grade_boot_source,
                "name": "web-server",
                "size": "15Gi",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirming that mariadb-server-vm exists",
                "task": self._grade_vm_exists,
                "name": "mariadb-server-vm",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm that dbadmin user is set on mariadb-server-vm",
                "task": self._grade_check_user,
                "user_name": "dbadmin",
                "vm_name": "mariadb-server-vm",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirming that web-server-vm exists",
                "task": self._grade_vm_exists,
                "name": "web-server-vm",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm that webadmin user is set on web-server-vm",
                "task": self._grade_check_user,
                "user_name": "webadmin",
                "vm_name": "web-server-vm",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirming that the web-server-vm has a tmpdata disk",
                "task": self._grade_vm_disk,
                "name": "web-server-vm",
                "pvc_name": "tmpdata",
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
                "label": f"Deleting the {NAMESPACE} project (be patient)",
                "task": self._delete_ge_namespace,
                "fatal": True,
            },
        ]
        userinterface.Console(items).run_items(action="Finishing")

    # Start tasks
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

        # Return status to abort lab execution when failed
        return item["failed"]

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
                    "text": f"The {NAMESPACE} namespace already exists, please delete it or run 'lab finish {self.__LAB__}' before starting the exercise."
                }
            ]
        return item["failed"]

    # Grading Tasks

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

    def _grade_template_exists(self, item):
        item["failed"] = False
        tmp_name = item["name"]

        if not self.resource_exists(
            "template.openshift.io/v1", "Template", tmp_name, NAMESPACE
        ):
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {tmp_name} VM does not exist in the {NAMESPACE} project."
                }
            ]

    def _grade_boot_source(self, item):
        item["failed"] = False
        tmp_name = item["name"]
        boot = item["name"].lower()
        size = item["size"]

        resource = self.resource_get(
            "template.openshift.io/v1", "Template", tmp_name, NAMESPACE
        )

        try:
            claim = (
                resource.objects[0]
                .spec.dataVolumeTemplates[0]
                .spec.source.pvc.get("name")
                .lower()
            )
            if str(claim) != boot:
                raise Exception("The boot source {} is incorrect.".format(claim))
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {tmp_name} template does not exist in the {NAMESPACE} project.".format(
                        str(e)
                    )
                }
            ]

        try:
            storage = (
                resource.objects[0]
                .spec.dataVolumeTemplates[0]
                .spec.storage.resources.requests.get("storage")
            )
            if str(storage) != size:
                raise Exception(
                    "The requested PVC size {} is incorrect".format(storage)
                )
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": "Requested PVC size is set to {}. Please work through the lab instructions.".format(
                        str(e)
                    )
                }
            ]
        return item["failed"]

    def _grade_check_user(self, item):
        """
        Check cloud-init settings for defined user
        """
        item["failed"] = False

        # try:
        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", item["vm_name"], NAMESPACE
        )
        volumes = resource.spec.template.spec.volumes[::-1]
        for v in volumes:
            try:
                userdata = v.cloudInitConfigDrive.get("userData")
                if item["user_name"] not in str(userdata):
                    raise Exception(
                        "The {} user not found in cloudInitNoCloud userData.".format(
                            item["user_name"]
                        )
                    )
            except Exception as e:
                item["failed"] = True
                item["msgs"] = [
                    {
                        "text": "{} Please work through the lab instructions.".format(
                            str(e)
                        )
                    }
                ]

            return item["failed"]

    def _grade_vm_disk(self, item):
        item["failed"] = False

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", item["name"], NAMESPACE
        )

        try:
            volumes = resource.spec.template.spec.volumes[1].name

            if item["pvc_name"] not in str(volumes):
                raise Exception(
                    "The {} volume was not found in the VM's manifest".format(
                        item["pvc_name"]
                    )
                )
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {"text": "{} Please work through the lab instructions.".format(str(e))}
            ]
        return item["failed"]

    # Finish Tasks

    def _delete_ge_namespace(self, item):
        item["failed"] = False
        try:
            self.delete_resource("v1", "Namespace", (NAMESPACE), "")
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [{"text": "Failed removing namespace: %s" % e}]
        if not item["failed"]:
            # Give time for the namespace to terminate
            time.sleep(120)
