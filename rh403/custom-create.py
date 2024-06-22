#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * May 24 2022 Trey Feagle <tfeagle@redhat.com>
#   - original code
# * Jun 21 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Aug 03 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - script enhances
# * Jan 03 2023 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 software.
This module implements the start and finish functions for the
Creating Custom Products and Repositories guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]
_targetl = ["localhost"]
_orgname_ops = "Operations"
_location = "Boston"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"

_productname = "Red Hat Enterprise Linux for x86_64"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/custom-create/"
_systemstats = "systemstats-1.0-1.el9.noarch.rpm"
_custom_prodname = "Custom Software"


labname = 'custom-create'

# Change the class name to match your file name.


class CustomCreate(GuidedExercise):
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


            steps.run_command(label=f"Removing product '{_custom_prodname}'",
                              hosts=_targets,
                              command="if [[ $(hammer product list"
                              + " --organization " + _orgname_ops
                              + " | grep '" + _custom_prodname + "') ]];"
                              + " then hammer product delete"
                              + " --name='" + _custom_prodname + "'"
                              + " --organization='" + _orgname_ops + "';"
                              + " exit 0; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Copying files",
                              hosts=_targetl,
                              command="cp "
                              + _basedir + _systemstats
                              + " /home/student/"
                              + _systemstats,
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
        ]
        Console(items).run_items(action="Finishing")
