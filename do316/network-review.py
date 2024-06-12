#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Mar 02 2022 Herve Quatremain <hquatrem@redhat.com>
#   - original code
# * May 06 2024 Andres Hernandez <andres.hernandez@redhat.com>
#   - Update to OCP 4.14
#   - Add load balancer service

"""
Grading module for DO316 network-review lab.
This module either does start, grade, or finish for the network-review lab.
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
NAMESPACE = "network-review"


# Disable certificate validation
disable_warnings(InsecureRequestWarning)


class NetworkReview(OpenShift):
    """
    Network Review lab script for DO316
    """

    __LAB__ = "network-review"

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
                "label": "Creating mariadb-server vm",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/mariadb-server.yml",
                "fatal": True,
            },
            {
                "label": "Creating front-web vm",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/front-web.yml",
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
                "label": "The mariadb-server VM has the 'tier=backend' label",
                "task": self._grade_vm_label,
                "name": "mariadb-server",
                "label_key": "tier",
                "label_value": "backend",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The 'database' ClusterIP service exists",
                "task": self._grade_service,
                "name": "database",
                "type": "ClusterIP",
                "selector_label_key": "tier",
                "selector_label_value": "backend",
                "port": 3306,
                "target_port": 3306,
                "proto": "TCP",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The network-review namespace has the 'allowed=database' label",
                "task": self._grade_namespace_label,
                "name": "network-review",
                "label_key": "allowed",
                "label_value": "database",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The allow-database network policy exists",
                "task": self._grade_network_policy,
                "name": "allow-database",
                "pod_label_key": "tier",
                "pod_label_value": "backend",
                "namespace_label_key": "allowed",
                "namespace_label_value": "database",
                "port": 3306,
                "proto": "TCP",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The front-web VM has the 'tier=frontend' label",
                "task": self._grade_vm_label,
                "name": "front-web",
                "label_key": "tier",
                "label_value": "frontend",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The 'web' ClusterIP service exists",
                "task": self._grade_service,
                "name": "web",
                "type": "ClusterIP",
                "selector_label_key": "tier",
                "selector_label_value": "frontend",
                "port": 8080,
                "target_port": 80,
                "proto": "TCP",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web application is reachable from outside",
                "task": self._grade_url_code,
                "url": "http://intranet-dev.apps.ocp4.example.com",
                "code": 200,
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web application can access the database",
                "task": self._grade_url_content,
                "url": "http://intranet-dev.apps.ocp4.example.com/cgi-bin/dbtest",
                "match": "PASS",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The 'ssh-web' LoadBalancer service exists",
                "task": self._grade_service,
                "name": "ssh-web",
                "type": "LoadBalancer",
                "selector_label_key": "kubevirt.io/domain",
                "selector_label_value": "front-web",
                "port": 22,
                "target_port": 22,
                "proto": "TCP",
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

    def _grade_vm_label(self, item):
        item["failed"] = False
        vmi_name = item["name"]

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachineInstance", vmi_name, NAMESPACE
        )

        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {vmi_name} VMI does not exist in the {NAMESPACE} project."
                }
            ]
            return

        key = item["label_key"]
        value = item["label_value"]
        v = resource.metadata.labels.get(key)
        if v is None:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {vmi_name} VMI does have a {key} label."}]
            return

        if v != value:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"Wrong value for the {key} label: got '{v}' instead of '{value}'."
                }
            ]

    def _grade_service(self, item):
        item["failed"] = False
        item["msgs"] = []
        service_name = item["name"]

        resource = self.resource_get("v1", "Service", service_name, NAMESPACE)
        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {service_name} service does not exist in the {NAMESPACE} project."
                }
            ]
            return

        service_type = item.get("type")
        if service_type:
            srv_t = resource.spec.type
            if srv_t.lower() != service_type.lower():
                item["failed"] = True
                item["msgs"].append(
                    {
                        "text": f"Wrong service type: got '{srv_t}' instead of '{service_type}'."
                    }
                )

        key = item["selector_label_key"]
        value = item["selector_label_value"]
        v = resource.spec.selector.get(key)
        if v is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The service does not use the {key} label for the selector."}
            )
        elif v != value:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"Wrong value for the {key} selector label: got '{v}' instead of '{value}'."
                }
            )

        port = item["port"]
        t_port = item["target_port"]
        proto = item.get("proto", "TCP")
        for ip in resource.spec.ports:
            p = ip.get("port")
            tp = ip.get("targetPort")
            pr = ip.get("protocol")
            if p == port and tp == t_port and pr == proto:
                break
        else:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"Cannot find the targeted port: {proto} port {port} with target port {t_port}."
                }
            )

    def _grade_namespace_label(self, item):
        item["failed"] = False
        namespace_name = item["name"]

        resource = self.resource_get("v1", "Namespace", namespace_name, "default")

        if resource is None:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {namespace_name} namespace does not exist."}]
            return

        key = item["label_key"]
        value = item["label_value"]
        v = resource.metadata.labels.get(key)
        if v is None:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {namespace_name} namespace does have a {key} label."}
            ]
            return

        if v != value:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"Wrong value for the {key} label: got '{v}' instead of '{value}'."
                }
            ]

    def _grade_network_policy(self, item):
        item["failed"] = False
        item["msgs"] = []
        policy_name = item["name"]

        resource = self.resource_get(
            "networking.k8s.io/v1", "NetworkPolicy", policy_name, NAMESPACE
        )
        if resource is None:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {policy_name} service does not exist in the {NAMESPACE} project."
                }
            ]
            return

        key = item["pod_label_key"]
        value = item["pod_label_value"]
        try:
            v = resource.spec.podSelector.matchLabels.get(key)
        except Exception:
            v = None
        if v is None:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"The network policy does not use the {key} label for the pod selector."
                }
            )
        elif v != value:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"Wrong value for the {key} pod selector label: got '{v}' instead of '{value}'."
                }
            )

        key = item["namespace_label_key"]
        value = item["namespace_label_value"]
        port = item["port"]
        proto = item.get("proto", "TCP")
        port_ok = False
        from_ok = False
        for ingress in resource.spec.ingress:
            for p in ingress.get("ports", []):
                if p.get("port") == port and p.get("protocol") == proto:
                    port_ok = True
                    break
            for f in ingress.get("from", []):
                try:
                    if f.namespaceSelector.matchLabels.get(key) == value:
                        from_ok = True
                        break
                except Exception:
                    pass
        if not port_ok:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"Cannot find {proto} port {port} in the ingress section."}
            )
        if not from_ok:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"Cannot find the source namespace '{key}: {value}' label in the ingress section."
                }
            )

    def _grade_url_code(self, item):
        item["failed"] = False
        url = item["url"]
        code = item.get("code", 200)

        request_response = requests.head(url)
        ret = request_response.status_code
        if ret != code:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"Cannot reach {url}: got HTTP reponse status {ret} instead of {code}."
                }
            ]

    def _grade_url_content(self, item):
        item["failed"] = False
        url = item["url"]
        expected_content = item["match"]

        request_response = requests.get(url)
        if expected_content not in request_response.text:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The returned data from {url} does not include '{expected_content}'."
                }
            ]
