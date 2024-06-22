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
# * Dec 14 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps


"""
Lab script for RH403 deploy.
This module implements the start and finish functions for the
Configure Organizations and Content Manifests guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]

_orgname_ops = "Operations"
_orgname_mkt = "Marketing"
_location = "Boston"
_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_manifest_ope = "manifest_operations.zip"
_manifest_mkt = "manifest_marketing.zip"


labname = 'deploy-manifest'

# Change the class name to match your file name.


class DeployManifest(GuidedExercise):
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
            newcourselib.verify_organization_cdn(_orgname_ops),
            newcourselib.check_manifest_in_workstation(_basedir, _manifest_ope),
            newcourselib.check_manifest_in_workstation(_basedir, _manifest_mkt),
            newcourselib.remove_location(_location),
            newcourselib.remove_org(_orgname_mkt),
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
