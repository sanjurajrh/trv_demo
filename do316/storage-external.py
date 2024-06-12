#
# Copyright (c) 2021, 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Fri Feb 25 2022 Herve Quatremain <hquatrem@redhat.com>
#   - adapt code for the specific GE

"""
Grading module for DO316 storage-external guided exercise.
This module either does start or finish for the storage-external guided exercise.
"""

import os
import sys
import time
import logging
import requests
import subprocess

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
NAMESPACES = ["storage-external"]
NAMESPACES_STR = " and ".join(NAMESPACES)

# Disable certificate validation
disable_warnings(InsecureRequestWarning)


# Change the class name to match your file name with WordCaps
class StorageExternal(OpenShift):
    """
    External storage GE script for DO316
    """

    __LAB__ = "storage-external"

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
                "label": f"Confirming the {NAMESPACES_STR} project does not exist",
                "task": self._check_ge_namespace,
                "fatal": True,
            },
            {
                "label": "Creating mariadb-server vm",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/mariadb-server.yml",
                "fatal": True,
            },
            {
                "label": "Copying exercise content",
                "task": labtools.copy_lab_files,
                "lab_name": self.__LAB__,
                "fatal": True,
            },
            {
                "label": "Confirming external iSCSI storage settings",
                "task": self._configure_iscsi,
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
                "label": f"Deleting the {NAMESPACES_STR} project (be patient)",
                "task": self._delete_ge_namespace,
                "fatal": True,
            },
            {
                "label": "Deleting the iscsi-pv persistent volume",
                "task": self._delete_ge_pv,
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
        item["msgs"] = []
        for x in NAMESPACES:
            if self.resource_exists("v1", "Namespace", (x), ""):
                item["failed"] = True
                item["msgs"].append(
                    {
                        "text": f"The {x} namespace already exists, please delete it or run 'lab finish {self.__LAB__}' before starting the exercise"
                    }
                )

        return item["failed"]

    def _delete_ge_namespace(self, item):
        item["failed"] = False
        for x in NAMESPACES:
            try:
                self.delete_resource("v1", "Namespace", (x), "")
            except Exception as e:
                item["failed"] = True
                item["msgs"] = [{"text": "Failed removing namespace %s: %s" % (x, e)}]
        if not item["failed"]:
            # Give time for the namespaces to terminate
            time.sleep(180)

    def _delete_ge_pv(self, item):
        item["failed"] = False
        try:
            self.delete_resource("v1", "PersistentVolume", "iscsi-pv", "")
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [{"text": "Failed removing the 'iscsi-pv' PV: %s" % e}]

    def _configure_iscsi(self, item):
        item["failed"] = False
        subprocess.run(
            [f"~/DO316/labs/{self.__LAB__}/files/iscsi_config.sh &> /dev/null"],
            shell=True,
            capture_output=False,
        )
