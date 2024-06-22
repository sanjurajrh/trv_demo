#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Mar 01 2022 Victor Costea <vcostea@redhat.com>
#   - original code
# * Jun 07 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Dec 20 2022 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps
# * Feb 07 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Check Marketing org exists.
#   - Remove lifecycle path in Marketing

"""
Lab script for RH403 lifecycles.
This module implements the start and finish functions for the
Create Software Lifecycles guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]
_orgname_ops = "Operations"
_orgname_mkt = "Marketing"
_orgdesc_mkt = "Marketing Department"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_manifest_mkt = "manifest_marketing.zip"

_lclib = "Library"
_lcdev = "Development"
_lcqa = "QA"
_lcprod = "Production"

_ops_cv = "OperationsServerBase"
_mkt_cv = "MarketingServerBase"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

labname = 'lifecycles-create'

# Change the class name to match your file name.


class LifecyclesCreate(GuidedExercise):
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

            newcourselib.verify_organization(_orgname_ops),
            newcourselib.verify_organization_cdn(_orgname_ops),

            newcourselib.check_organization(_orgname_mkt, _orgdesc_mkt),
            newcourselib.check_manifest_in_satellite(_basedir, _manifest_mkt),
            newcourselib.check_organization(_orgname_mkt, _orgdesc_mkt),
            newcourselib.check_manifest(_orgname_mkt, _manifest_mkt),
            newcourselib.verify_organization_cdn(_orgname_mkt),

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),
            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),

            newcourselib.remove_lifecycle_cv(_orgname_ops, _ops_cv, _lcprod),
            newcourselib.remove_lifecycle_cv(_orgname_ops, _ops_cv, _lcdev),
            newcourselib.remove_lifecycle_cv(_orgname_ops, _ops_cv, _lcqa),
            newcourselib.remove_lifecycle_cv(_orgname_ops, _ops_cv, _lclib),
            newcourselib.remove_cv(_orgname_ops, _ops_cv),
            newcourselib.remove_lifecycle_cv(_orgname_mkt, _ops_cv, _lcprod),
            newcourselib.remove_lifecycle_cv(_orgname_mkt, _ops_cv, _lcdev),
            newcourselib.remove_lifecycle_cv(_orgname_mkt, _ops_cv, _lcqa),
            newcourselib.remove_lifecycle_cv(_orgname_mkt, _ops_cv, _lclib),
            newcourselib.remove_cv(_orgname_mkt, _mkt_cv),

            newcourselib.remove_lifecycle(_orgname_ops, _lcprod),
            newcourselib.remove_lifecycle(_orgname_ops, _lcqa),
            newcourselib.remove_lifecycle(_orgname_ops, _lcdev),
            newcourselib.remove_lifecycle(_orgname_mkt, _lcprod),
            newcourselib.remove_lifecycle(_orgname_mkt, _lcqa),
            newcourselib.remove_lifecycle(_orgname_mkt, _lcdev),
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
