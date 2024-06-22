#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Apr 18 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Jun 09 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Dec 27 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps
# * Feb 21 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Update CV versions

"""
Lab script for RH403 software.
This module implements the start and finish functions for the
Control Software with Content Views guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "servera", "serverc"]
_host = ["satellite"]
_host_clienta = ["servera"]
_host_clientc = ["serverc"]
_host_clienta_fqdn = "servera.lab.example.com"
_host_clientc_fqdn = "serverc.lab.example.com"

_orgname_ops = "Operations"
_location = "Boston"

_lclib = "Library"
_lcdev = "Development"
_lcdevdesc = "Development"
_lcqa = "QA"
_lcqadesc = "Quality Assurance"
_lcprod = "Production"
_lcproddesc = "Production"

_ops_cv = "OperationsServerBase"

_env_dev = "Development/OperationsServerBase"
_packages = "ant"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"


labname = 'software-control'

# Change the class name to match your file name.


class SoftwareControl(GuidedExercise):
    """Activity class."""
    __LAB__ = labname

    def start(self):
        """
        Prepare systems for the lab exercise.
        """
        items = [
            newcourselib.verify_systems(_targets),
            newcourselib.satellite_status(),
            newcourselib.verify_default_organization(),
            newcourselib.verify_cdn_listing(),
            newcourselib.verify_organization_cdn(_orgname_ops),
            newcourselib.check_location(_location, _orgname_ops),
            newcourselib.check_default_org_loc(_orgname_ops, _location),

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),

            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),

            newcourselib.check_lifecycle(_orgname_ops, _lcdev, _lcdevdesc, _lclib),
            newcourselib.check_lifecycle(_orgname_ops, _lcqa, _lcqadesc, _lcdev),
            newcourselib.check_lifecycle(_orgname_ops, _lcprod, _lcproddesc, _lcqa),

            newcourselib.check_cvs_in_place(_orgname_ops, _ops_cv),

            newcourselib.check_host_cv(_orgname_ops, _ops_cv, _lcdev, _host_clienta_fqdn),
            newcourselib.check_host_cv(_orgname_ops, _ops_cv, _lcdev, _host_clientc_fqdn),
            newcourselib.register_host(_host_clienta, _orgname_ops, _env_dev),
            newcourselib.register_host(_host_clientc, _orgname_ops, _env_dev),
            newcourselib.remove_packages(_host_clienta, _packages),
            newcourselib.remove_packages(_host_clientc, _packages),
        ]
        Console(items).run_items(action="Starting")

    def finish(self):
        """
        Perform any post-lab cleanup tasks.
        """
        items = [
            newcourselib.verify_systems(_targets),
        ]
        Console(items).run_items(action="Finishing")
