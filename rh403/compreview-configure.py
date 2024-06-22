#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Aug 12 2022 Alex Callejas <acalleja@redhat.com>
#   - original code
# * Mar 01 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 comprehensive review.
This module implements the start, grade and finish functions for the
Red Hat Satellite configuration laboratory.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]

_orgname = "Marketing"
_locname = "San Francisco"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_manifest_mkt = "manifest_marketing.zip"

_repo_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS (RPMs)"
_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_productname = "Red Hat Enterprise Linux for x86_64"

_cvname = "MarketingServerBase"


labname = 'compreview-configure'

# Change the class name to match your file name.


class CompreviewConfigure(GuidedExercise):
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

            newcourselib.check_manifest_in_workstation(_basedir, _manifest_mkt),

            newcourselib.remove_org(_orgname),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label=f"Check '{_orgname}' organization",
                              hosts=["satellite"],
                              command="hammer organization info"
                                      + " --name '" + _orgname + "'",
                              student_msg=f"'{_orgname}' organization not found",
                              returns=0,
                              prints=f"Label:.*{_orgname}",
                              shell=True,
                              ),

            steps.run_command(label=f"Check '{_locname}' location",
                              hosts=["satellite"],
                              command="hammer location list"
                                      + " --organization '" + _orgname + "'"
                                      + " --fields=Name",
                              returns=0,
                              prints=_locname,
                              shell=True,
                              ),

            steps.run_command(label=f"Check '{_orgname}' CDN",
                              hosts=["satellite"],
                              command="hammer organization info"
                                      + " --name '" + _orgname + "' "
                                      + "--fields 'Cdn configuration/url'",
                              returns="0",
                              prints="http://cdn.lab.example.com",
                              shell=True
                              ),

            steps.run_command(label=f"Check lifecycle environment on '{_orgname}'",
                              hosts=["satellite"],
                              command="if [[ $(hammer lifecycle-environment paths "
                              + " --organization '" + _orgname + "'"
                              + " | grep 'Library >> Development >> QA >> Production' "
                              + ") ]]; then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label=f"Check '{_repo_base}' repository is synced",
                              hosts=["satellite"],
                              command="hammer repository info"
                                      + " --name '" + _repo_name_base + "'"
                                      + " --organization '" + _orgname + "'"
                                      + " --product '" + _productname + "'"
                                      + " --fields Sync/status"
                                      + " | grep Success",
                              student_msg=f"'{_repo_base}' repository is not synced",
                              returns=0,
                              shell=True
                              ),

            steps.run_command(label=f"Check '{_cvname}' content view",
                              hosts=["satellite"],
                              command="hammer content-view info"
                                      + " --name '" + _cvname + "'"
                                      + " --organization '" + _orgname + "'",
                              student_msg=f"'{_cvname}' content view not found",
                              returns=0,
                              prints=f"Label:.*{_cvname}",
                              shell=True
                              ),

            steps.run_command(label=f"Check '{_cvname}' content view repositories",
                              hosts=["satellite"],
                              command="hammer content-view info"
                                      + " --organization '" + _orgname + "'"
                                      + " --name '" + _cvname + "'"
                                      + " --fields 'Yum repositories/name'"
                                      + " | grep '" + _repo_name_base + "'",
                              student_msg=f"Repository not found in '{_cvname}' content view",
                              returns=0,
                              shell=True
                              ),

            steps.run_command(label=f"Check '{_cvname}' content view promotion",
                              hosts=["satellite"],
                              command="hammer content-view info"
                                      + " --organization '" + _orgname + "'"
                                      + " --name '" + _cvname + "'"
                                      + " --fields 'Lifecycle environments/name'"
                                      + " | grep Development",
                              student_msg=f"'{_cvname}' content view is not promoted in Development lc",
                              returns=0,
                              shell=True
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
