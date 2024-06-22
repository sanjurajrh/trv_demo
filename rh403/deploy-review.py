#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Feb 10 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Jun 06 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Sep 29 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Fixed manifest function
# * Dec 14 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 deploy.
This module implements the start, grade and finish functions for the
Plan and Deploy Red Hat Satellite laboratory.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]

_orgname_fin = "Finance"
_location_t = "Tokyo"
_location_sf = "San Francisco"
_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_manifest_fin = "manifest_finance.zip"

labname = 'deploy-review'

# Change the class name to match your file name.


class DeployReview(GuidedExercise):
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
            newcourselib.verify_cdn_listing(),
            newcourselib.verify_organization_cdn(_orgname_fin),
            newcourselib.check_manifest_in_workstation(_basedir, _manifest_fin),
            newcourselib.remove_location(_location_t),
            newcourselib.remove_location(_location_sf),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label="Verify Finance organization",
                              hosts=["satellite"],
                              command="hammer",
                              options=["--username", "admin", "--password",
                                       "redhat", "organization", "info",
                                       "--name", "Finance"],
                              student_msg="Finance organization not found",
                              returns=0,
                              prints="Label:.*Finance"
                              ),
            steps.run_command(label="Verify San Francisco location",
                              hosts=["satellite"],
                              command="hammer location list --organization 'Finance' --fields=Name",
                              returns=0,
                              prints="San Francisco",
                              shell=True,
                              ),
            steps.run_command(label="Verify Tokyo location",
                              hosts=["satellite"],
                              command="hammer location list --organization 'Finance' --fields=Name",
                              student_msg="Tokyo location not found",
                              returns=0,
                              prints="Tokyo",
                              shell=True,
                              ),
            steps.run_command(label="Verify subscriptions for Finance organization",
                              hosts=["satellite"],
                              command="hammer",
                              options=["--username", "admin", "--password",
                                       "redhat", "subscription", "list",
                                       "--organization", "Finance", "--fields",
                                       "Name,Quantity"],
                              student_msg="The subsciption is not loaded",
                              returns=0,
                              prints="Red Hat Enterprise Linux Server, Standard"
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
