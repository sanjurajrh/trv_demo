#
# Copyright 2022 Red Hat, Inc.
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Mon Jul 25 2022 Patrick Gomez <pagomez@redhat.com>
#   - update to Dynolabs
# * Feb 09 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 maintain-user.
This module implements the start and finish functions for the
chapter 12 user section guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise


_targets = ["satellite"]

_orgname = "Operations"
_location = "Boston"

_user01 = "user-admin"
_user02 = "intern034"
_role01 = "ops-user-admin"

# Change the class name to match your file name.
labname = 'maintain-user'


class RemoteConfigure(GuidedExercise):
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
            newcourselib.check_location(_location, _orgname),
            newcourselib.check_default_org_loc(_orgname, _location),

            newcourselib.remove_user(_user01),
            newcourselib.remove_user(_user02),
            newcourselib.remove_role(_role01),
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
