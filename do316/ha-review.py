#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Tue May 17th Natalie Lind <nlind@redhat.com>
#   - original code

"""
Grading module for DO316 ha-review guided exercise.
This module either does start, grade, or finish for the ha-review guided exercise.
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
NAMESPACE = "ha-review"

# Disable certificate validation
disable_warnings(InsecureRequestWarning)


class HAReview(OpenShift):
    """
    HA Review GE script for DO316
    """

    __LAB__ = "ha-review"

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
                "label": "Creating the www1 virtual machine",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/www1.yml",
                "fatal": True,
            },
            {
                "label": "Creating the www2 virtual machine",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/www2.yml",
                "fatal": True,
            },
            {
                "label": "Creating the mariadb-server virtual machine",
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
                "label": "The web service exists",
                "task": self._grade_service,
                "name": "web",
                "type": "ClusterIP",
                "selector_label_key": "app",
                "selector_label_value": "web",
                "port": 80,
                "target_port": 80,
                "proto": "TCP",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web application route is accessible",
                "task": self._grade_url_code,
                "url": "http://web-ha-review.apps.ocp4.example.com",
                "code": 200,
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The readiness probe is configured for www1",
                "task": self._grade_vm_readiness,
                "name": "www1",
                "path": "/health",
                "port": 80,
                "period": 5,
                "failures": 2,
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The watchdog device is configured on www2",
                "task": self._grade_vm_watchdog,
                "name": "www2",
                "action": "poweroff",
                "device_name": "testwatchdog",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The evictionStrategy is set on www2",
                "task": self._grade_eviction,
                "name": "www2",
                "strategy": "LiveMigrate",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The liveness probe is configured for mariadb-server",
                "task": self._grade_vm_liveness,
                "name": "mariadb-server",
                "port": 3306,
                "delay": 10,
                "period": 5,
                "fatal": False,
                "grading": True,
            },
            {
                "label": "Confirm that the worker node is cordoned off",
                "task": self._grade_node_cordon,
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
                "label": "Restoring cluster settings",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/restore.yml",
                "fatal": True,
            },
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
                    "text": f"Cannot reach {url}: got HTTP response status {ret} instead of {code}."
                }
            ]

    def _grade_vm_readiness(self, item):
        item["failed"] = False
        item["msgs"] = []
        vm_name = item["name"]
        path = item["path"]
        port = item["port"]
        period = item["period"]
        failures = item["failures"]

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        )

        try:
            readiness = resource.spec.template.spec.get("readinessProbe")
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]
            return

        if readiness is None:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"No readiness probe configured for the {vm_name} VM."}
            ]
            return

        http_get = readiness.get("httpGet")
        if http_get is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": "The readiness probe does not have an 'httpGet' section."}
            )
        else:
            r_path = http_get.get("path")
            if r_path is None:
                item["failed"] = True
                item["msgs"].append(
                    {
                        "text": "The path parameter is not set under the 'httpGet' section."
                    }
                )
            elif r_path != path:
                item["failed"] = True
                item["msgs"].append({"text": f"The path is not {path}: got {r_path}"})

            r_port = http_get.get("port")
            if r_port is None:
                item["failed"] = True
                item["msgs"].append(
                    {
                        "text": "The port parameter is not set under the 'httpGet' section."
                    }
                )
            elif r_port != port:
                item["failed"] = True
                item["msgs"].append({"text": f"The port is not {port}: got {r_port}"})

        r_period = readiness.get("periodSeconds")
        if r_period is None:

            item["failed"] = True
            item["msgs"].append({"text": "The periodSeconds parameter is not set."})
        elif r_period != period:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The periodSeconds parameter is not {period}: got {r_period}"}
            )

        r_failures = readiness.get("failureThreshold")
        if r_failures is None:

            item["failed"] = True
            item["msgs"].append({"text": "The failureThreshold parameter is not set."})
        elif r_failures != failures:
            item["failed"] = True
            item["msgs"].append(
                {
                    "text": f"The failureThreshold parameter is not {failures}: got {r_failures}"
                }
            )

    def _grade_vm_watchdog(self, item):
        item["failed"] = False
        item["msgs"] = []
        vm_name = item["name"]
        action = item["action"]
        device = item["device_name"]

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        )

        try:
            watchdog = resource.spec.template.spec.domain.devices.get("watchdog")
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]
            return

        if watchdog is None:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"No watchdog device configured for the {vm_name} VM."}
            ]
            return

        watch_action = watchdog.i6300esb.get("action")
        if watch_action is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": "The watchdog does not have an 'action' defined."}
            )
        else:
            if watch_action != action:
                item["failed"] = True
                item["msgs"].append(
                    {"text": f"The action is not {action}: got {watch_action}"}
                )
        watch_name = watchdog.get("name")
        if watch_name is None:
            item["failed"] = True
            item["msgs"].append({"text": "The watchdog device is not named."})
        elif watch_name != device:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The watch dog name is not {device}: got {watch_name}"}
            )

    def _grade_eviction(self, item):
        item["failed"] = False
        item["msgs"] = []
        vm_name = item["name"]
        strat = item["strategy"]

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        )

        try:
            evict = resource.spec.template.spec.get("evictionStrategy")
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]
            return

        if evict is None:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"No eviction strategy configured for the {vm_name} VM."}
            ]
            return

        if evict != strat:
            item["failed"] = True
            item["msgs"] - [
                {"text": f"The eviction strategy is not {strat}: got {evict}."}
            ]

    def _grade_vm_liveness(self, item):
        item["failed"] = False
        item["msgs"] = []
        vm_name = item["name"]
        port = item["port"]
        delay = item["delay"]
        period = item["period"]

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        )

        try:
            liveness = resource.spec.template.spec.get("livenessProbe")
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]
            return

        if liveness is None:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"No liveness probe configured for the {vm_name} VM."}
            ]
            return

        l_delay = liveness.get("initialDelaySeconds")
        if l_delay is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": "The initialDelaySeconds parameter is not set for the probe."}
            )
        elif l_delay != delay:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The initialDelaySeconds is not {delay}: got {l_delay}"}
            )

        p_seconds = liveness.get("periodSeconds")
        if p_seconds is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": "The periodSeconds parameter is not set for the probe."}
            )
        elif p_seconds != period:
            item["failed"] = True
            item["msgs"].append(
                {"text": f"The periodSeconds is not {period}: got {p_seconds}"}
            )

        p_port = liveness.tcpSocket.get("port")
        if p_port is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": "The port parameter is not set for the probe."}
            )
        elif p_port != port:
            item["failed"] = True
            item["msgs"].append({"text": f"The port is not {port}: got {p_port}"})

    def _grade_node_cordon(self, item):
        item["failed"] = False
        item["msgs"] = []
        node1 = "worker01"
        node2 = "worker02"

        resource1 = self.resource_get("v1", "Node", node1, "")
        sched1 = resource1.spec.get("unschedulable")

        resource2 = self.resource_get("v1", "Node", node2, "")
        sched2 = resource2.spec.get("unschedulable")

        if sched1 is None and sched2 is None:
            item["failed"] = True
            item["msgs"].append(
                {"text": "Workloads are schedulable on all cluster nodes"}
            )
        else:
            item["failed"] = False
            return
