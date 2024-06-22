#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Mar 22 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Jun 07 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Dec 15 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps
# * Feb 07 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Changed sync plan name

"""
Lab script for RH403 lifecycles.
This module implements the start and finish functions for the
Synchronize Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]

_orgname_ops = "Operations"
_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"
_syncplan = "Red Hat Products - Operations"

labname = 'lifecycles-sync'

# Change the class name to match your file name.


class LifecyclesSync(GuidedExercise):
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

            newcourselib.remove_repository(_orgname_ops, _repo_name_tools, _productname),
            newcourselib.remove_sync_plan(_orgname_ops, _syncplan),
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
