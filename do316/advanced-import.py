#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Apr 10 2024 Francois Andrieu <fandrieu@redhat.com>
#   - original code

"""
Grading module for DO316 advanced-import guided exercise.
This module either does start or finish for the advanced-import guided exercise.
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
NAMESPACE = "vms-import"

# Disable certificate validation
disable_warnings(InsecureRequestWarning)


# Change the class name to match your file name with WordCaps
class AdvancedImport(OpenShift):
    """
    Migration toolkit for virtualization GE script for DO316
    """

    __LAB__ = "advanced-import"

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
            # TODO: Remove MTV if already installed
            {
                "label": "Verifying migration toolkit for virtualization requirements",
                "task": self._fix_cluster_proxy,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Preparing the utility system for the exercise",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/add_ova_image.yml",
                "fatal": True,
            },
            {
                "label": "Verifying OpenShift Virtualization Operator",
                "task": common.openshift_virt,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Verifying Kubernetes NMState Operator",
                "task": common.nmstate_operator,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Configuring additional vm network",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/add_net.yml",
                "fatal": True,
            },
            {
                "label": f"Confirming that the {NAMESPACE} project does not exist",
                "task": self._check_ge_namespace,
                "fatal": True,
            },
            {
                "label": f"Creating the {NAMESPACE} project",
                "task": self._create_ge_namespace,
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
                "label": "Cleaning the utility system",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/remove_ova_image.yml",
                "fatal": True,
            },
            {
                "label": f"Deleting the {NAMESPACE} project",
                "task": self._delete_ge_namespace,
                "fatal": True,
            },
            {
                "label": "Removing VM network",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/remove_net.yml",
                "fatal": True,
            },
            {
                "label": "Removing the MTV operator",
                "task": self._delete_mtv,
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

    def _create_ge_namespace(self, item):
        """
        Create GE namespace
        """
        item["failed"] = False
        try:
            body = {
                "apiVersion": "project.openshift.io/v1",
                "kind": "Project",
                "metadata": {
                    "name": (NAMESPACE),
                },
            }
            logging.info("Create {}/{}".format(body["kind"], body["metadata"]["name"]))
            resource = self.oc_client.resources.get(
                api_version=body["apiVersion"], kind=body["kind"]
            )
            resource.create(body=body, namespace=None)
        except Exception as e:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"Could not create the project, please run 'lab finish {self.__LAB__} to cleanup the environment and start the lab again."
                }
            ]
            item["exception"] = {
                "name": e.__class__.__name__,
                "message": str(e),
            }
        return item["failed"]

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

    def _fix_cluster_proxy(self, item):

        item["failed"] = False
        proxyAPI = self.oc_client.resources.get(
            api_version="config.openshift.io/v1", kind="Proxy"
        )
        cluster_proxy = proxyAPI.get(name="cluster")

        body = {
            "apiVersion": "config.openshift.io/v1",
            "kind": "Proxy",
            "metadata": {
                "name": "cluster",
            },
            "spec": {"trustedCA": {"name": ""}},
        }

        try:
            if (
                "trustedCA" not in cluster_proxy.spec
                or "name" not in cluster_proxy.spec.trustedCA
            ):
                proxyAPI.patch(body=body, content_type="application/merge-patch+json")
            else:
                pass
        except Exception as e:
            import traceback

            print(traceback.format_exc())
            raise e

    # Finish Tasks

    def _delete_ge_namespace(self, item):

        item["failed"] = False

        try:
            ns = self.oc_client.resources.get(
                api_version="v1",
                kind="Namespace",
            )
            if ns.get(name=NAMESPACE):
                ns.delete(name=NAMESPACE)
                for t in range(120):
                    time.sleep(1)
                    if not ns.get(name=NAMESPACE):
                        break

        except ApiException as e:
            if e.status != 404:
                raise e

        except Exception as e:
            item["failed"] = True
            item["msgs"] = [{"text": "Failed removing namespace: %s" % e}]

    def _delete_mtv(self, item):
        item["failed"] = False
        item["msgs"] = []

        try:
            fc = self.oc_client.resources.get(
                api_version="console.openshift.io/v1",
                kind="ConsolePlugin",
            )
            if fc.get(name="forklift-console-plugin"):
                fc.delete(name="forklift-console-plugin", namespace="")
                for t in range(60):
                    time.sleep(1)
                    if not fc.get(name="forklift-console-plugin"):
                        break

            if fc.get(name="forklift-console-plugin"):
                raise Exception(
                    "forklift-console-plugin is not deleted after 60 seconds"
                )

        except ApiException as e:
            if e.status != 404:
                raise e

        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {"text": "Failed removing forklift-console-plugin resource: %s" % e}
            )
            return

        try:
            ns = self.oc_client.resources.get(
                api_version="v1",
                kind="Namespace",
            )
            if ns.get(name="openshift-mtv"):
                ns.delete(name="openshift-mtv")
                for t in range(120):
                    time.sleep(1)
                    if not ns.get(name="openshift-mtv"):
                        break

            if ns.get(name="openshift-mtv"):
                raise Exception("openshift-mtv namespace not deleted after 120 seconds")

        except ApiException as e:
            if e.status != 404:
                raise e

        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {"text": "Failed removing namespace openshift-mtv: %s" % (e,)}
            )
            return

        try:
            crds = {
                "forkliftcontrollers.forklift.konveyor.io",
                "hooks.forklift.konveyor.io",
                "hosts.forklift.konveyor.io",
                "migrations.forklift.konveyor.io",
                "networkmaps.forklift.konveyor.io",
                "openstackvolumepopulators.forklift.konveyor.io",
                "ovirtvolumepopulators.forklift.konveyor.io",
                "plans.forklift.konveyor.io",
                "providers.forklift.konveyor.io",
                "storagemaps.forklift.konveyor.io",
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
                    "text": "Failed removing custom resource definitions for the migration toolkit for virtualization: %s"
                    % e
                }
            )

        pv_api = self.oc_client.resources.get(api_version="v1", kind="PersistentVolume")
        pvs = pv_api.get()
        for pv in pvs.items:
            if pv.status.phase == "Released":
                pv_api.delete(name=pv.metadata.name)
