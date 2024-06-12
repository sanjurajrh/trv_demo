#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Apr 1, 2022 Natalie Lind <nlind@redhat.com>
#

"""
Grading module for DO316 accessing-review guided exercise.
This module implements the start, grading, and finish actions for the accessing-review lab.
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
    "localhost",
]

# Default namespace for the resources
NAMESPACE = ["vm-images", "staging-db", "development-db"]

# Disable certificate validation
disable_warnings(InsecureRequestWarning)


# Change the class name to match your file name with WordCaps
class AccessingReview(OpenShift):
    """
    Accessing Review GE script for DO316
    """

    __LAB__ = "accessing-review"

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
                "label": "Confirming that the exercise projects do not exist",
                "task": self._check_ge_namespace,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Creating exercise users",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/create-users.yml",
                "fatal": True,
            },
            {
                "label": "Creating exercise resources (please be patient)",
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
                "label": "Confirm admin rolebindings for the database-admins group",
                "task": self._grade_rolebinding,
                "role_name": "admin",
                "role_project": f"{NAMESPACE[1]}",
                "group_or_user": "database-admins",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm view rolebinding for the developer user",
                "task": self._grade_rolebinding,
                "role_name": "view",
                "role_project": f"{NAMESPACE[2]}",
                "group_or_user": "developer",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm that staging-mariadb exists and is stopped in the staging-db project",
                "task": self._grade_vm_exists,
                "vm_name": "staging-mariadb",
                "vm_namespace": "staging-db",
                "vm_status": "Stopped",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm that dbadmin2 user is set on staging-mariadb",
                "task": self._grade_check_user,
                "user_name": "dbadmin2",
                "vm_name": "staging-mariadb",
                "vm_namespace": "staging-db",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm CPU and memory increase on staging-mariadb",
                "task": self._grade_vm_resources,
                "vm_name": "staging-mariadb",
                "vm_namespace": "staging-db",
                "memory": "4Gi",
                "cpu_cores": "2",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm that dev-mariadb does not exist in the development-db project",
                "task": self._grade_vm_deleted,
                "vm_name": "dev-mariadb",
                "vm_project": "development-db",
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
                "label": f"Deleting the {NAMESPACE} projects (please wait)",
                "task": self._delete_ge_namespace,
                "fatal": True,
            },
            {
                "label": "Deleting exercise users",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/delete-users.yml",
                "fatal": True,
            },
            {
                "label": "Remove exercise files",
                "task": labtools.delete_workdir,
                "lab_name": self.__LAB__,
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

        # Return status to abort lab execution when failed
        return item["failed"]

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
        # projects = ["development-db", "staging-db", "vm-images"]

        for x in NAMESPACE:
            try:
                self.resource_exists("v1", "Namespace", (x), "")
            except Exception as e:
                item["failed"] = True
                item["msgs"] = [
                    {
                        "text": f"The {x} namespace already exists, please delete it or run 'lab finish {self.__LAB__}' before starting this lab."
                        % e
                    }
                ]
                return item["failed"]

    # Grading Tasks

    def _grade_rolebinding(self, item):
        """
        Check for rolebindings
        """
        item["failed"] = False
        role = item["role_name"]
        project = item["role_project"]
        group_user = item["group_or_user"]

        resource = self.resource_get(
            "rbac.authorization.k8s.io/v1", "RoleBinding", role, project
        )

        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {role} does not exist in the {project} namespace."}
            ]
            return

        subjects = resource.subjects[0].get("name")
        if subjects is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {role} in {project} namespace does not have defined subjects."
                }
            ]
            return

        if subjects != group_user:
            item["Failed"] = True
            item["msgs"] = [
                {"text": f"{group_user} does not have {role} permissions in {project}."}
            ]
            return

    def _grade_vm_exists(self, item):
        """
        Confirm that the VM exists
        """
        item["failed"] = False
        if self.resource_exists(
            "kubevirt.io/v1", "VirtualMachine", item["vm_name"], item["vm_namespace"]
        ):
            item["failed"] = False
        else:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": "The {} does not exist in {}; please work through the lab instructions.".format(
                        item["vm_name"], item["vm_namespace"]
                    )
                }
            ]
            return item["failed"]
        try:
            resource = self.resource_get(
                "kubevirt.io/v1",
                "VirtualMachine",
                item["vm_name"],
                item["vm_namespace"],
            )
            status = resource.status.printableStatus

            if status != str(item["vm_status"]):
                raise Exception("The status of the {} vm incorrect.".format(status))
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {"text": "{} Please work through the lab instructions.".format(str(e))}
            ]
        return item["failed"]

    def _grade_check_user(self, item):
        """
        Check cloud-init settings for defined user
        """
        item["failed"] = False

        try:
            resource = self.resource_get(
                "kubevirt.io/v1",
                "VirtualMachine",
                item["vm_name"],
                item["vm_namespace"],
            )
            userdata = resource.spec.template.spec.volumes[1].cloudInitNoCloud.userData

            if item["user_name"] not in str(userdata):
                raise Exception(
                    "The {} user not found in cloudInitNoCloud userData.".format(
                        item["user_name"]
                    )
                )
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {"text": "{} Please work throgh the lab instructions.".format(str(e))}
            ]
        return item["failed"]

    def _grade_vm_resources(self, item):
        """
        Confirm 4Gi memory and 2 CPU cores on VM
        """
        item["failed"] = False
        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", item["vm_name"], item["vm_namespace"]
        )
        try:
            cores = resource.spec.template.spec.domain.cpu.get("cores")
            if str(cores) != item["cpu_cores"]:
                raise Exception("{} CPU cores is incorrect".format(cores))
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": "CPU core is set to {}. Please work through the lab instructions.".format(
                        str(e)
                    )
                }
            ]
        try:
            req_mem = resource.spec.template.spec.domain.memory.get("guest")
            if str(req_mem) != item["memory"]:
                raise Exception("{} requested memory is incorrect".format(req_mem))
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": "Memory is set to {}. Please work through the lab instructions.".format(
                        str(e)
                    )
                }
            ]
        return item["failed"]

    def _grade_vm_deleted(self, item):
        """
        Confirm that the VM does not exist
        """
        item["failed"] = False
        try:
            if self.resource_exists(
                "kubevirt.io/v1", "VirtualMachine", item["vm_name"], item["vm_project"]
            ):
                raise Exception(
                    "Found {} in the {}.".format(item["vm_name"], item["vm_project"])
                )
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {"text": "{} Please work through the lab instructions.".format(str(e))}
            ]
        return item["failed"]

    # Finish Tasks

    def _delete_ge_namespace(self, item):
        """
        Delete lab namespaces
        """
        item["failed"] = False
        projects = ["development-db", "staging-db", "vm-images"]

        for x in projects:
            try:
                self.delete_resource("v1", "Namespace", (x), "")
            except Exception as e:
                item["failed"] = True
                item["msgs"] = [{"text": "Failed removing namespace: %s" % e}]
            if not item["failed"]:
                time.sleep(30)
