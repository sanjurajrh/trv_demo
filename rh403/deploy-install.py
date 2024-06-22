#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jan 20 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Jun 06 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Dec 14 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 deploy.
This module implements the start and finish functions for the
Verify a Red Hat Satellite Installation guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]

labname = 'deploy-install'

# Change the class name to match your file name.


class DeployInstall(GuidedExercise):
    """Activity class."""
    __LAB__ = labname

    def start(self):
        """
        Prepare systems for the lab exercise.
        """
        items = [
            newcourselib.verify_systems(_targets),
            newcourselib.satellite_status(),
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
