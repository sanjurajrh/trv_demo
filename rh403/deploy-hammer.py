#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jul 19 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - original code
# * Sep 29 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Changed lab name, added Operations organization
# * Dec 14 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 deploy.
This module implements the start and finish functions for the
Deploy Hammer guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "capsule"]
_host = ["satellite"]

_orgname_ops = "Operations"
_orgname_fin = "Finance"
_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_base_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS RPMs 8"
_repo_name_app_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8"
_productname = "Red Hat Enterprise Linux for x86_64"

_orgname = "SecOps"
_col_fire = "Firewalls"
_col_ids = "IDS"
_col_logs = "LogServers"

labname = 'deploy-hammer'

# Change the class name to match your file name.


class DeployHammer(GuidedExercise):
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
            newcourselib.verify_default_location(),
            newcourselib.verify_organization(_orgname_ops),
            newcourselib.verify_organization(_orgname_fin),
            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base_rhel8, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app_rhel8, _productname),
            newcourselib.remove_collection(_orgname, _col_fire),
            newcourselib.remove_collection(_orgname, _col_ids),
            newcourselib.remove_collection(_orgname, _col_logs),
            newcourselib.remove_org(_orgname),
            steps.run_command(label="Check exercise file is not present",
                              hosts=_host,
                              command="rm -Rf /root/satellite*log",
                              returns="0",
                              shell=True
                              ),
        ]
        Console(items).run_items(action="Starting")

    def finish(self):
        """
        Perform any post-lab cleanup tasks.
        """
        items = [
            newcourselib.verify_systems(_targets),
            newcourselib.remove_org(_orgname),
        ]
        Console(items).run_items(action="Finishing")
