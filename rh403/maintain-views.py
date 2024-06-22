#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Aug 08 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Feb 10 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 maintain.
This module implements the start and finish functions for the
Maintain views.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]
_host = ["satellite"]

_orgname = "Operations"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

_lclib = "Library"
_lcdev = "Development"
_lcdevdesc = "Development"
_lcqa = "QA"
_lcqadesc = "Quality Assurance"
_lcprod = "Production"
_lcproddesc = "Production"

_ops_cv = "OperationsServerBase"
_ops_cv_desc = "Base Packages"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/maintain-views/"
_script = "check_cv_versions.sh"

_exports = "/var/lib/pulp/exports/*"
_download_policy = "on_demand"


labname = 'maintain-views'

# Change the class name to match your file name.


class MaintainViews(GuidedExercise):
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
            newcourselib.verify_organization_cdn(_orgname),

            newcourselib.check_sync_product_repos(_orgname, _productname),
            newcourselib.verify_repository(_orgname, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname, _repo_name_app, _productname),
            newcourselib.check_repo_added(_repo_tools, _orgname, _release),
            newcourselib.check_sync_repo(_orgname, _repo_name_tools, _productname),

            newcourselib.check_lifecycle(_orgname, _lcdev, _lcdevdesc, _lclib),
            newcourselib.check_lifecycle(_orgname, _lcqa, _lcqadesc, _lcdev),
            newcourselib.check_lifecycle(_orgname, _lcprod, _lcproddesc, _lcqa),

            newcourselib.check_cv(_orgname, _ops_cv, _ops_cv_desc),
            newcourselib.check_repo_cv(_orgname, _ops_cv, _repo_name_base),
            newcourselib.check_publish_cv(_orgname, _ops_cv, _ops_cv_desc, _lclib),
            newcourselib.check_promote_cv(_orgname, _ops_cv, _ops_cv_desc, _lcdev),
            newcourselib.check_file_in_satellite(_basedir, _script),
            newcourselib.check_script(_host, _script),

            newcourselib.remove_file_directory(_host, _exports),
            newcourselib.check_download_policy(_orgname, _repo_name_base, _download_policy),
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
