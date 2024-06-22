#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Sep 21 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - original code
# * Feb 02 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 api.
This module implements the start and finish functions for the
Api Ansible guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]

_orgname_ops = "Operations"
_orgname_fin = "Finance"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_ansibletar_name = "redhat-satellite-3.6.0.tgz"
_ansibletar_loc = _basedir + _ansibletar_name
_to_host = "workstation"
_dest = "/home/student/"

labname = 'api-ansible'

# Change the class name to match your file name.


class ApiHammer(GuidedExercise):
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
            newcourselib.verify_organization_cdn(_orgname_fin),

            newcourselib.copy_file(_to_host, _ansibletar_loc, _dest),
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
