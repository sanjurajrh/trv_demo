#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Thu Apr 28 2022 Herve Quatremain <hquatrem@redhat.com>
#   - original code

"""
Grading module for DO316 review-cr1 lab.
This module either does start, grade, or finish for the review-cr1 lab.
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
NAMESPACE = "review-cr1"


# Disable certificate validation
disable_warnings(InsecureRequestWarning)


class ReviewCR1(OpenShift):
    """
    Comprehensive review 3 script for DO316
    """

    __LAB__ = "review-cr1"

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
                "label": "Confirming virtctl availability",
                "task": self.run_playbook,
                "playbook": "ansible/roles/deploy-virtctl.yml",
                "fatal": True,
            },
            {
                "label": "Removing OpenShift Virtualization",
                "task": self._delete_virtualization,
                "fatal": True,
            },
            {
                "label": "Verifying Kubernetes NMState Operator",
                "task": common.nmstate_operator,
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
                "label": "The OpenShift Virtualization Operator is installed",
                "task": self._grade_virtualization,
                "name": "openshift-cnv",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The worker01 node has the 'orgnet: true' label",
                "task": self._grade_node_label,
                "name": "worker01",
                "label_key": "orgnet",
                "label_value": "true",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The worker02 node has the 'orgnet: true' label",
                "task": self._grade_node_label,
                "name": "worker02",
                "label_key": "orgnet",
                "label_value": "true",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The NodeNetworkConfigurationPolicy object exists",
                "task": self._grade_node_network,
                "name": "br0",
                "port": "ens4",
                "label_key": "orgnet",
                "label_value": "true",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The ext-net network attachment resource exists",
                "task": self._grade_attachment,
                "name": "ext-net",
                "bridge": "br0",
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
                "label": "The web1 VM was created from the RHEL8 template",
                "task": self._grade_vm_template,
                "name": "web1",
                "template": "rhel8-server-small",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web1 VM has a nic-0 network interface",
                "task": self._grade_vm_nic,
                "name": "web1",
                "nic": "nic-0",
                "attachment": "ext-net",
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
                "label": "Reverting nodes' network settings",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/finish_network.yml",
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

    def _delete_virtualization(self, item):
        item["failed"] = False
        item["msgs"] = []

        try:
            try:
                hco = self.oc_client.resources.get(
                    api_version="hco.kubevirt.io/v1beta1",
                    kind="HyperConverged",
                )
            except Exception:
                item["msgs"] = [{"text": "HyperConverged does not exist"}]
                return

            if len(hco.get().items):
                hco.delete(name="kubevirt-hyperconverged", namespace="openshift-cnv")
                # gives 300 sec to remove the hco (this can take a long time on a slow cluster)
                for t in range(300):
                    time.sleep(1)
                    if len(hco.get().items) == 0:
                        break

            if len(hco.get().items):
                raise Exception("HyperConverged is not deleted after 120 seconds")

        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": "Failed removing kubevirt-hyperconverged HyperConverged resource from the openshift-cnv project: %s"
                    % e
                }
            )
            # don't go any further if the hco is not deleted
            return

        # try:
        #    self.delete_resource(
        #        "operators.coreos.com/v1alpha1",
        #        "Subscription",
        #        "hco-operatorhub",
        #        "openshift-cnv",
        #    )
        # except Exception as e:
        #    item["failed"] = True
        #    item["msgs"].append(
        #        {
        #            "text": "Failed removing hco-operatorhub subscription from the openshift-cnv project: %s"
        #            % e
        #        }
        #    )

        try:
            self.delete_resource(
                "operators.coreos.com/v1alpha1",
                "Subscription",
                "kubevirt-hyperconverged",
                "openshift-cnv",
            )
        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": "Failed removing kubevirt-hyperconverged subscription from the openshift-cnv project: %s"
                    % e
                }
            )

        try:
            self.delete_resource(
                "operators.coreos.com/v1alpha1",
                "ClusterServiceVersion",
                "kubevirt-hyperconverged-operator.v4.14.1",
                "openshift-cnv",
            )
        except Exception as e:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": "Failed removing kubevirt-hyperconverged-operator.v4.14.1 cluster service version from the openshift-cnv project: %s"
                    % e
                }
            )

        try:
            ns = self.oc_client.resources.get(
                api_version="v1",
                kind="Namespace",
            )
            if ns.get(name="openshift-cnv"):
                ns.delete(name="openshift-cnv")
                for t in range(120):
                    time.sleep(1)
                    if ns.get(name="openshift-cnv"):
                        continue

            if ns.get(name="openshift-cnv"):
                raise Exception("openshift-cnv namespace not deleted after 120 seconds")

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
                "cdis.cdi.kubevirt.io",
                "hostpathprovisioners.hostpathprovisioner.kubevirt.io",
                "hyperconvergeds.hco.kubevirt.io",
                "kubevirts.kubevirt.io",
                "networkaddonsconfigs.networkaddonsoperator.network.kubevirt.io",
                "ssps.ssp.kubevirt.io",
                "tektontasks.tektontasks.kubevirt.io",
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
                    "text": "Failed removing custom resource definitions for OpenShift Virtualization: %s"
                    % e
                }
            )

        # time.sleep(15)

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

    def _grade_virtualization(self, item):
        item["failed"] = False
        namespace = item["name"]

        if not self.resource_exists("v1", "Namespace", namespace, ""):
            item["failed"] = True
            item["msgs"] = [{"text": f"The {namespace} namespace does not exist."}]
            return

        if not self.resource_exists(
            "operators.coreos.com/v1alpha1",
            "Subscription",
            "kubevirt-hyperconverged",
            namespace,
        ):
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The kubevirt-hyperconverged subscription resource does not exist in the {namespace} namespace."
                }
            ]
            return

        if not self.resource_exists(
            "hco.kubevirt.io/v1beta1",
            "HyperConverged",
            "kubevirt-hyperconverged",
            namespace,
        ):
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The HyperConverged instance does not exist in the {namespace} namespace."
                }
            ]

    def _grade_node_label(self, item):
        item["failed"] = False
        node_name = item["name"]

        resource = self.resource_get("v1", "Node", node_name, "")

        if resource is None:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {node_name} node does not exist."}]
            return

        key = item["label_key"]
        value = item["label_value"]
        v = resource.metadata.labels.get(key)
        if v is None:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {node_name} node does have a {key} label."}]
            return

        if v != value:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"Wrong value for the {key} label: got '{v}' instead of '{value}'."
                }
            ]

    def _grade_node_network(self, item):
        item["failed"] = False
        item["msgs"] = []
        br_name = item["name"]
        port = item["port"]
        key = item["label_key"]
        value = item["label_value"]

        resources = self.oc_client.resources.get(
            api_version="nmstate.io/v1", kind="NodeNetworkConfigurationPolicy"
        )
        nncps = resources.get()
        for nncp in nncps.items:
            try:
                if nncp.spec.nodeSelector.get(key) is not None:
                    break
            except Exception:
                pass
        else:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"There is no NodeNetworkConfigurationPolicy resource that selects the '{key}: {value}' nodes."
                }
            ]
            return

        v = nncp.spec.nodeSelector.get(key)
        if v != value:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"Wrong value for the {key} node selector: got '{v}' instead of '{value}'."
                }
            )

        for interface in nncp.spec.desiredState.interfaces:
            if interface.name == br_name:
                break
        else:
            item["failed"] = True
            item["msgs"].append({"text": f"The {br_name} bridge is not declared."})
            return

        if interface.type != "linux-bridge":
            item["failed"] = True
            item["msgs"].append({"text": "The interface type is not 'linux-bridge'."})

        try:
            for p in interface.bridge.port:
                if p.get("name") == port:
                    return
            else:
                item["failed"] = True
                item["msgs"].append(
                    {
                        "text": f"The {port} interface is not connected to the {br_name} bridge."
                    }
                )
        except Exception:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"The {port} interface is not connected to the {br_name} bridge."
                }
            )

    def _grade_attachment(self, item):
        item["failed"] = False
        name = item["name"]
        bridge = item["bridge"]

        resource = self.resource_get(
            "k8s.cni.cncf.io/v1", "NetworkAttachmentDefinition", name, NAMESPACE
        )
        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {name} network attachment definition resource does not exist in the {NAMESPACE} project."
                }
            ]
            return

        res = resource.metadata.annotations.get("k8s.v1.cni.cncf.io/resourceName")
        if res is None or bridge not in res:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {name} network attachment definition resource does not use the {bridge} bridge."
                }
            ]

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

    def _grade_vm_nic(self, item):
        item["failed"] = False
        vm_name = item["name"]
        nic = item["nic"]
        attachment = item["attachment"]

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        )

        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]
            return

        for net in resource.spec.template.spec.networks:
            name = net.get("name")
            if name is not None and name.lower() == nic.lower():
                break
        else:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {nic} network interface does not exist."}]
            return

        try:
            name = net.multus.networkName
            if name == attachment:
                return
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {nic} network interface does not have an attachment."}
            ]
            return

        item["failed"] = True
        item["msgs"] = [
            {
                "text": f"The {nic} network interface does not use the {attachment} attachment: got {name} instead."
            }
        ]
