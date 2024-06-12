#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Dec 05 2022 Herve Quatremain <hquatrem@redhat.com>
#   - removing ens4 configuration on worker nodes (Jira DO316-25)
# * Dec 12 2021 Natalie Lind <nlind@redhat.com>
#   - original code

"""
Grading module for DO316 multihomed-nmstate guided exercise.
This module either does start or finish for the multihomed-nmstate guided exercise.
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
NAMESPACE = "developer-vms"

# Disable certificate validation
disable_warnings(InsecureRequestWarning)


# Change the class name to match your file name with WordCaps
class MultihomedNmstate(OpenShift):
    """
    Multihomed NMState GE script for DO316
    """

    __LAB__ = "multihomed-nmstate"

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
                "label": "Verifying worker node settings",
                "task": self.run_playbook,
                "playbook": "ansible/roles/verify-worker-nodes.yml",
                "fatal": True,
            },
            {
                "label": "Disabling ens4 on worker nodes",
                "task": self.run_playbook,
                "playbook": "ansible/roles/disable-ens4.yml",
                "fatal": True,
            },
            {
                "label": f"Confirming that the {NAMESPACE} project does not exist",
                "task": self._check_ge_namespace,
                "fatal": True,
            },
            {
                "label": "Creating exercise resources",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/dev-dbaccess-vm.yml",
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
                "label": "Reverting Worker01/02 network settings and labels",
                "task": self.run_playbook,
                "playbook": "ansible/roles/verify-worker-nodes.yml",
                "fatal": True,
            },
            {
                "label": f"Deleting the {NAMESPACE} project",
                "task": self._delete_ge_namespace,
                "fatal": True,
            },
            {
                "label": "Remove nmstate operator",
                "task": self._delete_nmstate_operator,
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
        if self.resource_exists("v1", "Namespace", (NAMESPACE), ""):
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {NAMESPACE} namespace already exists, please delete it or run 'lab finish {self.__LAB__}' before starting the exercise."
                }
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
            time.sleep(60)

    def _delete_nmstate_operator(self, item):
        item["failed"] = False
        item["msgs"] = []

        try:
            self.delete_resource(
                "operators.coreos.com/v1alpha1",
                "Subscription",
                "kubernetes-nmstate-operator",
                "openshift-nmstate",
            )
        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": "Failed removing nmstate subscription from the openshift-nmstate project: %s"
                    % e
                }
            )

        try:
            self.delete_resource(
                "operators.coreos.com/v1alpha1",
                "ClusterServiceVersion",
                "kubernetes-nmstate-operator.4.14.0-202401081210",
                "openshift-nmstate",
            )
        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": "Failed removing kubernetes-nmstate-operator.4.14.0-202401081210 cluster service version from the openshift-nmstate project: %s"
                    % e
                }
            )

        try:
            ns = self.oc_client.resources.get(
                api_version="v1",
                kind="Namespace",
            )
            if ns.get(name="openshift-nmstate"):
                ns.delete(name="openshift-nmstate")
                for t in range(120):
                    time.sleep(1)
                    if ns.get(name="openshift-nmstate"):
                        continue

            if ns.get(name="openshift-nmstate"):
                raise Exception(
                    "openshift-nmstate namespace not deleted after 120 seconds"
                )

        except ApiException as e:
            if e.status != 404:
                raise e

        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {"text": "Failed removing namespace %s: %s" % (NAMESPACE, e)}
            )
            return

        try:
            crds = {
                "nmstates.nmstate.io",
            }
            for crd in crds:
                self.delete_resource(
                    "apiextensions.k8s.io",
                    "customresourcedefinition",
                    (crd),
                    "",
                )
        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": "Failed removing custom resource definitions for NMstate: %s"
                    % e
                }
            )

        try:
            self.delete_resource(
                "console.openshift.io/v1",
                "ConsolePlugin",
                "nmstate-console-plugin",
                "",
            )
        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {"text": "Failed removing nmstate console plug-in: %s" % e}
            )
