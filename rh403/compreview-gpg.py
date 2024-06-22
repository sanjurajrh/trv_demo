#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Aug 22 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - original code
# * Mar 02 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 comprehensive review.
This module implements the start, grade and finish functions for the
Red Hat Satellite compreview laboratory.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]
_workstation_host = ["workstation"]

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_to_host = "workstation"
_dest = "/home/student/"
_gpgkey_name = "key.asc"
_gpgkey_loc = _basedir + _gpgkey_name
_rpm_name = "sm-practice-1.0-1.el9.x86_64.rpm"
_rpm_loc = _basedir + _rpm_name

_packages = "rpm-sign"
_dir_gnupg = "/home/student/.gnupg"
_dir_rpmmacros = "/home/student/.rpmmacros"


labname = 'compreview-gpg'

# Change the class name to match your file name.


class CompreviewGpg(GuidedExercise):
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

            newcourselib.copy_file(_to_host, _gpgkey_loc, _dest),
            newcourselib.copy_file(_to_host, _rpm_loc, _dest),

            # newcourselib.remove_packages(_workstation_host, _packages),
            steps.run_command(label="Remove rpm-sign package in workstation",
                              hosts=["localhost"],
                              command="ssh root@workstation"
                                      + " 'yum -y remove " + _packages + "'",
                              returns=0,
                              shell=True,
                              ),
            newcourselib.remove_file_directory(_workstation_host, _dir_rpmmacros),
            newcourselib.remove_file_directory(_workstation_host, _dir_gnupg),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),

            steps.run_command(label="Verify GPG key is installed",
                              hosts=["localhost"],
                              command="gpg --fingerprint"
                                      + " student@workstation.lab.example.com",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify RPM package is signed",
                              hosts=["localhost"],
                              command="rpm -qip ~/sm-practice-1.0-1.el9.x86_64.rpm |"
                              + " grep 'Signature' | grep 'Key ID'",
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
