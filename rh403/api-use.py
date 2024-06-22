#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jul 18 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code

"""
Lab script for RH403 api.
This module implements the start and finish functions for the
Integrate Red Hat Satellite Functionality in Applications guided exercise.
"""

from . import courselib
from labs.common import steps
from labs.common import labtools
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]
_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_template_py = "create-objects.py"
_template_rb = "create-objects.rb"
_tpy_loc = _basedir + "api-use/" + _template_py
_trb_loc = _basedir + "api-use/" + _template_rb
_orgname1 = "Sales"
_orgname2 = "Research"

labname = 'api-use'

# Change the class name to match your file name.


class ApiUse(GuidedExercise):
    """Activity class."""
    __LAB__ = labname

    def start(self):
        """
        Prepare systems for the lab exercise.
        """
        items = [
            {
                "label": "Checking lab systems",
                "task": labtools.check_host_reachable,
                "hosts": _targets,
                "fatal": True
            },
            courselib.satellite_status(),
            steps.run_command(label="Create bin directory",
                              hosts=["satellite"],
                              command="if [ ! -d ~/bin ]; then mkdir ~/bin; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Copy the create-objects.py file",
                              hosts=["localhost"],
                              command="scp " + _tpy_loc
                              + " root@satellite:" + "bin/" + _template_py,
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Ensure the create-objects.py file is executable",
                              hosts=["satellite"],
                              command="chmod +x ~/bin/" + _template_py,
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Copy the create-objects.rb file",
                              hosts=["localhost"],
                              command="scp " + _trb_loc
                              + " root@satellite:" + "bin/" + _template_rb,
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Ensure the create-objects.rb file is executable",
                              hosts=["satellite"],
                              command="chmod +x ~/bin/" + _template_rb,
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
            {
                "label": "Checking lab systems",
                "task": labtools.check_host_reachable,
                "hosts": _targets,
                "fatal": True
            },
            courselib.satellite_status(),

            courselib.remove_org(_targets, _orgname1),
            courselib.remove_org(_targets, _orgname2),
            steps.run_command(label="Remove bin directory",
                              hosts=["satellite"],
                              command="if [ -d ~/bin ]; then rm -rf ~/bin; fi",
                              returns="0",
                              shell=True
                              ),
        ]
        Console(items).run_items(action="Finishing")
