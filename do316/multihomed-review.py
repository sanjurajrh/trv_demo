#
# Copyright (c) 2021, 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * March 24 2022 Natalie Lind <nlind@redhat.com>
#   - original code

"""
Grading module for DO316 multihomed-review guided exercise.
This module either does start, grading, or finish for the multihomed-review guided exercise.
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
NAMESPACE = "multihomed-review"

# Disable certificate validation
disable_warnings(InsecureRequestWarning)


# Change the class name to match your file name with WordCaps
class MultihomedReview(OpenShift):
    """
    Multihomed Review lab script for DO316
    """

    __LAB__ = "multihomed-review"

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
                "label": "Verifying Kubernetes NMState Operator",
                "task": common.nmstate_operator,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Verify worker node settings",
                "task": self.run_playbook,
                "playbook": "ansible/roles/verify-worker-nodes.yml",
                "fatal": True,
            },
            {
                "label": f"Confirming that the {NAMESPACE} project does not exist",
                "task": self._check_ge_namespace,
                "oc_client": self.oc_client,
                "fatal": True,
            },
            {
                "label": "Creating the dev-external virtual machine",
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
                "label": "Check for NNCP and configured port",
                "task": self._grade_nncp_port,
                "policy_name": "br0-ens4-policy",
                "port_name": "ens4",
                "bridge_name": "br0",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Check NNCE status for worker nodes",
                "task": self._grade_nnce_status,
                "worker01_policy": "worker01.br0-ens4-policy",
                "worker02_policy": "worker02.br0-ens4-policy",
                "host1_name": "worker01",
                "host2_name": "worker02",
                "status": "True",
                "type": "Available",
                "reason": "SuccessfullyConfigured",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Check for the br0-network net-attach-def",
                "task": self._grade_nad,
                "nad_name": "br0-network",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm that the VM is running",
                "task": self._grade_vm_running,
                "name": "dev-external",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm that the VM is connected to the bridge",
                "task": self._grade_vm_bridge,
                "name": "dev-external",
                "bridge_name": "br0-network",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm that the VM has a 192.168.51.20 static IP address",
                "task": self._grade_vm_ip,
                "name": "dev-external",
                "ip": "192.168.51.20",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Test connectivity to VM from external network",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/ping_test.yml",
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
                "label": f"Deleting the {NAMESPACE} project (please wait)",
                "task": self._delete_ge_namespace,
                "fatal": True,
            },
            {
                "label": "Reverting Worker01-02 network settings and labels",
                "task": self.run_playbook,
                "playbook": "ansible/roles/verify-worker-nodes.yml",
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
                    "text": f"The {NAMESPACE} namespace already exists, please delete it or run 'lab finish {self.__LAB__}' before starting the exercise"
                }
            ]
        return item["failed"]

    # Grading Tasks

    def _grade_nncp_port(self, item):
        item["failed"] = False
        policy_name = item["policy_name"]
        port_name = item["port_name"]
        bridge_name = item["bridge_name"]

        resource = self.resource_get(
            "nmstate.io/v1", "NodeNetworkConfigurationPolicy", policy_name, ""
        )
        try:
            interfaces = resource.spec.desiredState.interfaces
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {policy_name} policy does not exist in the cluster."}
            ]
            return

        for i in interfaces:
            try:
                port = i.bridge.port.name.lower()
            except Exception:
                continue
            if port == port_name:
                break
        for i in interfaces:
            try:
                name = i.name.lower()
            except Exception:
                continue
            if name == bridge_name:
                break
        else:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {port_name} port is not specified in the policy."}
            ]

    def _grade_nnce_status(self, item):
        policy1_name = item["worker01_policy"]
        policy2_name = item["worker02_policy"]
        policy_type = item["type"]
        policy_reason = item["reason"]
        policy_status = item["status"]
        host1 = item["host1_name"]
        host2 = item["host2_name"]

        resource1 = self.resource_get(
            "nmstate.io/v1beta1", "NodeNetworkConfigurationEnactment", policy1_name, ""
        )
        resource2 = self.resource_get(
            "nmstate.io/v1beta1", "NodeNetworkConfigurationEnactment", policy2_name, ""
        )

        if resource1 is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {policy1_name} enactment for {host1} was not found in the cluster."
                }
            ]
            return

        type1 = resource1.status.conditions[2].get("type")
        reason1 = resource1.status.conditions[2].get("reason")
        status1 = resource1.status.conditions[2].get("status")

        if (
            status1 == policy_status
            and type1 == policy_type
            and reason1 == policy_reason
        ):
            return
        else:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {policy1_name} was not successful."}]

        if resource2 is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {policy2_name} enactment for {host2} was not found in the cluster."
                }
            ]
            return

        type2 = resource1.status.conditions[2].get("type")
        reason2 = resource1.status.conditions[2].get("reason")
        status2 = resource1.status.conditions[2].get("status")

        if (
            status2 == policy_status
            and type2 == policy_type
            and reason2 == policy_reason
        ):
            return
        else:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {policy2_name} was not successful."}]

    def _grade_nad(self, item):
        item["failed"] = False
        nad_name = item["nad_name"]

        if not self.resource_exists(
            "k8s.cni.cncf.io/v1", "NetworkAttachmentDefinition", nad_name, NAMESPACE
        ):
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": "The %s %s does not exist, please work through the lab instructions."
                    % (item["name"], item["type"])
                }
            ]
        return item["failed"]

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

    def _grade_vm_bridge(self, item):
        item["failed"] = False
        vmi_name = item["name"]
        bridge_name = item["bridge_name"].lower()

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachineInstance", vmi_name, NAMESPACE
        )
        try:
            networks = resource.spec.networks
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vmi_name} VM is not connected to a network."}
            ]
            return

        for n in networks:
            try:
                name = n.multus.networkName.lower()
            except Exception:
                continue
            if name == bridge_name:
                break
        else:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {bridge_name} bridge is not attached to the VM."}
            ]

    def _grade_vm_ip(self, item):
        item["failed"] = False
        vmi_name = item["name"]
        ip_add = item["ip"]

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachineInstance", vmi_name, NAMESPACE
        )

        try:
            ip_address = resource.status.interfaces[1].ipAddress
        except Exception:
            item["failed"] = True
            item["mesg"] = [
                {"text": f"Secondary interface missingg from the {vmi_name} VM."}
            ]
            return

        if ip_address.lower() != ip_add:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vmi_name} is not configured with the {ip_add} address."}
            ]

    # Finish Tasks

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
