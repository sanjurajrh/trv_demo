#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Mar 19 2022 Victor Costea <vcostea@redhat.com>
#   - original code
# * Jun 07 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Sep 25 2022 Alex Callejas <acalleja@redhat.com>
#   - add steps to change the lifecycle of a host
# * Dec 15 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps
# * Feb 07 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Remove check RHEL 9 Client repository synced in Marketing

"""
Lab script for RH403 lifecycles.
This module implements the start and finish functions for the
Publish and Promote Content Views guided exercise.
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

_liblc = "Library"
_devlc = "Development"
_devdesc = "Development"
_qalc = "QA"
_qadesc = "Quality Assurance"
_prodlc = "Production"
_proddesc = "Production"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

_ops_cv = "OperationsServerBase"
_mkt_cv = "MarketingServerBase"

labname = 'lifecycles-publish'

# Change the class name to match your file name.


class LifecyclesPublish(GuidedExercise):
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

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),
            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),

            newcourselib.check_lifecycle(_orgname_ops, _devlc, _devdesc, _liblc),
            newcourselib.check_lifecycle(_orgname_ops, _qalc, _qadesc, _devlc),
            newcourselib.check_lifecycle(_orgname_ops, _prodlc, _proddesc, _qalc),

            newcourselib.check_manifest_in_workstation(_basedir, _manifest_mkt),
            newcourselib.check_manifest_in_satellite(_basedir, _manifest_mkt),
            newcourselib.check_organization(_orgname_mkt, _orgdesc_mkt),
            newcourselib.check_manifest(_orgname_mkt, _manifest_mkt),
            newcourselib.verify_organization_cdn(_orgname_mkt),

            newcourselib.check_lifecycle(_orgname_mkt, _devlc, _devdesc, _liblc),
            newcourselib.check_lifecycle(_orgname_mkt, _qalc, _qadesc, _devlc),
            newcourselib.check_lifecycle(_orgname_mkt, _prodlc, _proddesc, _qalc),

            newcourselib.remove_cv(_orgname_ops, _ops_cv),
            newcourselib.remove_cv(_orgname_mkt, _mkt_cv),
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
