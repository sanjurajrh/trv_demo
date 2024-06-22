#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Mar 22 2022 Victor Costea <vcostea@redhat.com>
#   - original code
# * Jun 07 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Dec 21 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 lifecycles.
This module implements the start, grade and finish functions for the
Manage Software Lifecycles review lab.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]
_orgname_fin = "Finance"

_devlc = "Build"
_qalc = "Test"
_prodlc = "Deploy"
_fin_cv = "FinanceServerBase"
_syncplan = "Red Hat Products - Finance"

_repo_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS (RPMs)"
_repo_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream (RPMs)"
_release = "9"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

labname = 'lifecycles-review'

# Change the class name to match your file name.


class LifecyclesReview(GuidedExercise):
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
            newcourselib.verify_organization_cdn(_orgname_fin),

            newcourselib.check_sync_product_repos(_orgname_fin, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_app, _productname),

            # newcourselib.remove_repository(_orgname_fin, _repo_name_tools, _productname),
            newcourselib.remove_sync_plan(_orgname_fin, _syncplan),
            newcourselib.remove_lifecycle(_orgname_fin, _prodlc),
            newcourselib.remove_lifecycle(_orgname_fin, _qalc),
            newcourselib.remove_lifecycle(_orgname_fin, _devlc),
            newcourselib.remove_cv(_orgname_fin, _fin_cv),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label="Verify AppStream software repository",
                              hosts=_targets,
                              command="hammer"
                              + " repository-set list "
                              + " --organization " + _orgname_fin
                              + " --enabled True"
                              + " | grep 'Red Hat Enterprise Linux 9 for x86_64 - AppStream (RPMs)'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify BaseOS software repository",
                              hosts=_targets,
                              command="hammer"
                              + " repository-set list "
                              + " --organization " + _orgname_fin
                              + " --enabled True"
                              + " | grep 'Red Hat Enterprise Linux 9 for x86_64 - BaseOS (RPMs)'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify Satellite Client software repository",
                              hosts=_targets,
                              command="hammer"
                              + " repository-set list "
                              + " --organization " + _orgname_fin
                              + " --enabled True"
                              + " | grep 'Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify AppStream sync status",
                              hosts=_targets,
                              command="hammer"
                              + " repository info --name='" + _repo_name_app + "'"
                              + " --product='" + _productname + "'"
                              + " --organization='" + _orgname_fin + "'"
                              + " --fields 'Name,Sync/status' "
                              + " | grep 'Status:.*Success'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify BaseOS sync status",
                              hosts=_targets,
                              command="hammer"
                              + " repository info --name='" + _repo_name_app + "'"
                              + " --product='" + _productname + "'"
                              + " --organization='" + _orgname_fin + "'"
                              + " --fields 'Name,Sync/status' "
                              + " | grep 'Status:.*Success'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify Satellite Client sync status",
                              hosts=_targets,
                              command="hammer"
                              + " repository info --name='" + _repo_name_tools + "'"
                              + " --product='" + _productname + "'"
                              + " --organization='" + _orgname_fin + "'"
                              + " --fields 'Name,Sync/status' "
                              + " | grep 'Status:.*Success'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify sync plan for Red Hat Product",
                              hosts=_targets,
                              command="hammer"
                              + " sync-plan list "
                              + " --organization " + _orgname_fin
                              + " --fields Name "
                              + " | grep '" + _syncplan + "'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify environment path for organization: " + _orgname_fin,
                              hosts=_targets,
                              command="hammer"
                              + " lifecycle-environment paths "
                              + " --organization " + _orgname_fin
                              + " | grep 'Build.*>>.*Test.*>>.*Deploy'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify content view with associated repository",
                              hosts=_targets,
                              command="hammer"
                              + " content-view info "
                              + " --name='" + _fin_cv + "'"
                              + " --organization='" + _orgname_fin + "'"
                              + " --fields 'Yum repositories/name'"
                              + " | grep 'BaseOS RPMs'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify content view publish version",
                              hosts=_targets,
                              command="hammer"
                              + " content-view info "
                              + " --name='" + _fin_cv + "'"
                              + " --organization='" + _orgname_fin + "'"
                              + " --fields 'Versions/version'"
                              + " | grep '1.0'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify content view promotion to lifecycle environment",
                              hosts=_targets,
                              command="hammer"
                              + " content-view info"
                              + " --name='" + _fin_cv + "'"
                              + " --organization='" + _orgname_fin + "'"
                              + " --fields 'Lifecycle environments/name'"
                              + " | grep Build",
                              returns=0,
                              shell=True,
                              ),
        ]
        ui = Console(items)
        ui.run_items(action="Grading")
        ui.report_grade()

    def finish(self):
        """
        Perform any post-lab cleanup tasks.
        """
        items = [
            newcourselib.verify_systems(_targets),
        ]
        Console(items).run_items(action="Finishing")
