#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Mon Apr 25 2022 Herve Quatremain <hquatrem@redhat.com>
#   - original code

"""
Grading module for DO316 review-cr3 lab.
This module either does start, grade, or finish for the review-cr3 lab.
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
NAMESPACE = "review-cr3"


# Disable certificate validation
disable_warnings(InsecureRequestWarning)


class ReviewCR3(OpenShift):
    """
    Comprehensive review 1 script for DO316
    """

    __LAB__ = "review-cr3"

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
                "label": "Preparing the disk images on utility",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/start_image.yml",
                "fatal": True,
            },
            {
                "label": "Creating the data volumes",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/start_data_volumes.yml",
                "fatal": True,
            },
            {
                "label": "Creating the golden-web virtual machine",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/golden-web.yml",
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
                "label": "The web1 VM is running",
                "task": self._grade_vm_running,
                "name": "web1",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web2 VM is running",
                "task": self._grade_vm_running,
                "name": "web2",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web1-snap1 snapshot exists",
                "task": self._grade_vm_snapshot_exists,
                "name": "web1-snap1",
                "vm_name": "web1",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The readiness probe is configured for web1",
                "task": self._grade_vm_readiness,
                "name": "web1",
                "path": "/cgi-bin/health",
                "port": 80,
                "period": 5,
                "failures": 2,
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The readiness probe is configured for web2",
                "task": self._grade_vm_readiness,
                "name": "web2",
                "path": "/cgi-bin/health",
                "port": 80,
                "period": 5,
                "failures": 2,
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web1-documentroot PVC is connected to web1",
                "task": self._grade_vm_pvc,
                "name": "web1",
                "pvc_name": "web1-documentroot",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web2-documentroot PVC is connected to web2",
                "task": self._grade_vm_pvc,
                "name": "web2",
                "pvc_name": "web2-documentroot",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web1 VM has the 'tier: front' label",
                "task": self._grade_vm_label,
                "name": "web1",
                "label_key": "tier",
                "label_value": "front",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web2 VM has the 'tier: front' label",
                "task": self._grade_vm_label,
                "name": "web2",
                "label_key": "tier",
                "label_value": "front",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The front service exists",
                "task": self._grade_service,
                "name": "front",
                "type": "ClusterIP",
                "selector_label_key": "tier",
                "selector_label_value": "front",
                "port": 80,
                "target_port": 80,
                "proto": "TCP",
                "fatal": False,
                "grading": True,
            },
            {
                "label": "The web application is reachable from outside",
                "task": self._grade_url_code,
                "url": "http://front-review-cr3.apps.ocp4.example.com",
                "code": 200,
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
                "label": "Removing the disk images form utility",
                "task": self.run_playbook,
                "playbook": f"ansible/{self.__LAB__}/finish_image.yml",
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

    def _grade_vm_snapshot_exists(self, item):
        item["failed"] = False
        snap_name = item["name"]
        vm_name = item["vm_name"]

        resource = self.resource_get(
            "snapshot.kubevirt.io/v1alpha1",
            "VirtualMachineSnapshot",
            snap_name,
            NAMESPACE,
        )

        try:
            vm = resource.spec.source.name
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {snap_name} snapshot does not exist in the {NAMESPACE} project."
                }
            ]
            return

        if vm != vm_name:
            item["failed"] = True
            item["msgs"] = [
                {
                    "text": f"The {snap_name} snapshot is not a snapshot of the {vm_name} VM: it is a snapshot of {vm}."
                }
            ]

    def _grade_vm_pvc(self, item):
        item["failed"] = False
        vm_name = item["name"]
        pvc_name = item["pvc_name"].lower()

        resource = self.resource_get(
            "kubevirt.io/v1", "VirtualMachine", vm_name, NAMESPACE
        )

        try:
            volumes = resource.spec.template.spec.volumes
        except Exception:
            item["failed"] = True
            item["msgs"] = [
                {"text": f"The {vm_name} VM does not exist in the {NAMESPACE} project."}
            ]
            return

        for v in volumes:
            try:
                pvc = v.persistentVolumeClaim.claimName.lower()
            except Exception:
                continue
            if pvc == pvc_name:
                break
        else:
            item["failed"] = True
            item["msgs"] = [{"text": f"The {pvc_name} PVC is not attached to the VM."}]

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
