import time
import os
import sys
import logging
import pkg_resources

from labs import labconfig
from labs.common import labtools, userinterface
from ocp import utils
from ocp.utils import OpenShift

# from openshift.dynamic import DynamicClient
from openshift.dynamic.exceptions import (
    NotFoundError,
    ResourceNotFoundError,
    ForbiddenError,
    InternalServerError,
)
from kubernetes.client.exceptions import ApiException


def _wait_hyperconverged_ready(c):
    a, k, n = "hco.kubevirt.io/v1beta1", "HyperConverged", "openshift-cnv"
    s, t = 0, 600
    ready = "False"
    while ready == "False":
        try:
            r = c.resources.get(api_version=a, kind=k)
        except InternalServerError:
            s += 1
            continue
        if s > t:
            raise TimeoutError
        time.sleep(s)
        for i in r.get(kind=k, namespace=n)["items"]:
            try:
                for j in i["status"]["conditions"]:
                    if j["type"] == "Available":
                        ready = j["status"]
            except TypeError:
                pass
        s += s * 1.2 + 1


def _wait_nmstate_ready(c):
    s, t = 0, 600
    ready = "False"
    while ready == "False":
        try:
            r = c.resources.get(api_version="apps/v1", kind="Deployment")
        except InternalServerError:
            s += 1
            continue
        if s > t:
            raise TimeoutError
        time.sleep(s)
        for i in r.get(namespace="openshift-nmstate")["items"]:
            try:
                for j in i["status"]["conditions"]:
                    if j["type"] == "Available":
                        ready = j["status"]
            except TypeError:
                pass
        s += s * 1.2 + 1


def _wait_node_maintenance_ready(c):
    s, t = 0, 600
    ready = "False"
    while ready == "False":
        try:
            r = c.resources.get(api_version="apps/v1", kind="Deployment")
        except InternalServerError:
            s += 1
            continue
        if s > t:
            raise TimeoutError
        time.sleep(s)
        for i in r.get(namespace="openshift-workload-availability")["items"]:
            try:
                for j in i["status"]["conditions"]:
                    if j["type"] == "Available":
                        ready = j["status"]
            except TypeError:
                pass
        s += s * 1.2 + 1


def _patch_hco(c):
    a, k, ns, n = (
        "hco.kubevirt.io/v1beta1",
        "HyperConverged",
        "openshift-cnv",
        "kubevirt-hyperconverged",
    )
    hco = c.resources.get(api_version=a, kind=k).get(namespace=ns, name=n)

    body = {
        "kind": "HyperConverged",
        "apiVersion": "hco.kubevirt.io/v1beta1",
        "metadata": {
            "name": "kubevirt-hyperconverged",
        },
        "spec": {"featureGates": {"enableCommonBootImageImport": False}},
    }
    try:
        featureG = hco.spec.featureGates.enableCommonBootImageImport
        if featureG is True:
            c.resources.get(api_version=a, kind=k).patch(
                namespace=ns, body=body, content_type="application/merge-patch+json"
            )
        else:
            pass
    except Exception as e:
        import traceback

        print(traceback.format_exc())
        raise e


def _install(c, b):
    a, k = b["apiVersion"], b["kind"]
    s, t = 0, 600
    while True:
        if s > t:
            raise TimeoutError
        time.sleep(s)
        try:
            r = c.resources.get(api_version=a, kind=k)
            if k == "Project":
                n = b["metadata"]["name"]
                try:
                    r.get(name=n)
                except NotFoundError:
                    r.create(body=b, namespace=None)
            else:
                n = b["metadata"]["namespace"]
                if not r.get(kind=k, namespace=n)["items"]:
                    r.create(body=b, namespace=n)
            break
        except (NotFoundError, ResourceNotFoundError, ForbiddenError, ApiException):
            s += s * 1.2 + 1


def _current_csv(c, operator):
    a, k = "packages.operators.coreos.com/v1", "PackageManifest"
    n = "openshift-marketplace"
    r = c.resources.get(api_version=a, kind=k)
    return r.get(name=operator, namespace=n).status.channels[0].currentCSV


def openshift_virt(item):
    item["failed"] = False
    try:
        oc_client = item["oc_client"]
    except Exception as e:
        item["failed"] = True
        item["msgs"] = [{"text": "Must define oc_client within item: %s" % e}]
    try:
        components = [
            {
                "apiVersion": "project.openshift.io/v1",
                "kind": "Project",
                "metadata": {
                    "name": "openshift-cnv",
                    "namespace": None,
                },
            },
            {
                "apiVersion": "operators.coreos.com/v1",
                "kind": "OperatorGroup",
                "metadata": {
                    "name": "kubevirt-hyperconverged-group",
                    "namespace": "openshift-cnv",
                },
                "spec": {"targetNamespaces": ["openshift-cnv"]},
            },
            {
                "apiVersion": "operators.coreos.com/v1alpha1",
                "kind": "Subscription",
                "metadata": {"name": "hco-operatorhub", "namespace": "openshift-cnv"},
                "spec": {
                    "source": "do316-catalog-cs",
                    "sourceNamespace": "openshift-marketplace",
                    "name": "kubevirt-hyperconverged",
                    "startingCSV": _current_csv(oc_client, "kubevirt-hyperconverged"),
                    "channel": "stable",
                },
            },
            {
                "apiVersion": "hco.kubevirt.io/v1beta1",
                "kind": "HyperConverged",
                "metadata": {
                    "name": "kubevirt-hyperconverged",
                    "namespace": "openshift-cnv",
                },
            },
        ]
        for i in components:
            _install(oc_client, i)

        _wait_hyperconverged_ready(oc_client)
        _patch_hco(oc_client)

    except Exception as e:
        item["failed"] = True
        item["msgs"] = [{"text": "Failed installing OpenShift Virtualization: %s" % e}]
    return item["failed"]


def node_maintenance(item):
    item["failed"] = False
    try:
        oc_client = item["oc_client"]
    except Exception as e:
        item["failed"] = True
        item["msgs"] = [{"text": "Must define oc_client within item: %s" % e}]
    try:
        components = [
            {
                "apiVersion": "project.openshift.io/v1",
                "kind": "Project",
                "metadata": {
                    "name": "openshift-workload-availability",
                    "namespace": None,
                },
            },
            {
                "apiVersion": "operators.coreos.com/v1",
                "kind": "OperatorGroup",
                "metadata": {
                    "name": "openshift-workload-availability",
                    "namespace": "openshift-workload-availability",
                },
            },
            {
                "apiVersion": "operators.coreos.com/v1alpha1",
                "kind": "Subscription",
                "metadata": {
                    "name": "node-maintenance-operator",
                    "namespace": "openshift-workload-availability",
                },
                "spec": {
                    "source": "do316-catalog-cs",
                    "sourceNamespace": "openshift-marketplace",
                    "name": "node-maintenance-operator",
                    "startingCSV": _current_csv(oc_client, "node-maintenance-operator"),
                    "channel": "stable",
                },
            },
        ]
        for i in components:
            _install(oc_client, i)

        _wait_node_maintenance_ready(oc_client)

    except Exception as e:
        item["failed"] = True
        item["msgs"] = [{"text": "Failed installing Node Maintenance Operator: %s" % e}]
    return item["failed"]


def nmstate_operator(item):
    item["failed"] = False
    try:
        oc_client = item["oc_client"]
    except Exception as e:
        item["failed"] = True
        item["msgs"] = [{"text": "Must define oc_client within item: %s" % e}]
    try:
        components = [
            {
                "apiVersion": "project.openshift.io/v1",
                "kind": "Project",
                "metadata": {
                    "name": "openshift-nmstate",
                    "namespace": None,
                },
            },
            {
                "apiVersion": "operators.coreos.com/v1",
                "kind": "OperatorGroup",
                "metadata": {
                    "name": "openshift-nmstate",
                    "namespace": "openshift-nmstate",
                },
                "spec": {"targetNamespaces": ["openshift-nmstate"]},
            },
            {
                "apiVersion": "operators.coreos.com/v1alpha1",
                "kind": "Subscription",
                "metadata": {
                    "name": "kubernetes-nmstate-operator",
                    "namespace": "openshift-nmstate",
                },
                "spec": {
                    "source": "do316-catalog-cs",
                    "sourceNamespace": "openshift-marketplace",
                    "name": "kubernetes-nmstate-operator",
                    "startingCSV": _current_csv(
                        oc_client, "kubernetes-nmstate-operator"
                    ),
                    "channel": "stable",
                },
            },
            {
                "apiVersion": "nmstate.io/v1",
                "kind": "NMState",
                "metadata": {"name": "nmstate", "namespace": None},
            },
        ]
        for i in components:
            _install(oc_client, i)

        _wait_nmstate_ready(oc_client)

    except Exception as e:
        item["failed"] = True
        item["msgs"] = [
            {"text": "Failed installing Kubernetes NMState Operator: %s" % e}
        ]
    return item["failed"]
