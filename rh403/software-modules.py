#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * May 12 2022 Alex Callejas <acalleja@redhat.com>
#   - original code
# * Jun 10 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11

"""
Lab script for RH403 content host register.
This module implements the start and finish functions for the
Synchronize Red Hat Content guided exercise.
"""

from . import courselib
from labs.common import steps
from labs.common import labtools
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

# Vars

_targets = ["satellite"]
_orgname = "Operations"
_orgdesc = _orgname + " Department"
_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_manifest_name = "manifest_operations.zip"
_manifest_loc = _basedir + _manifest_name
_manifest = "/root/" + _manifest_name
_locname = "Boston"

_productname = "Red Hat Enterprise Linux for x86_64"
_liblc = "Library"
_devlc = "Development"
_devdesc = "Development"
_qalc = "QA"
_qadesc = "Quality Assurance"
_prodlc = "Production"
_proddesc = "Production"

_cvbase = "Base"
_cvbasedesc = "Base Packages"

_repo_base = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS (RPMs)"
_release_base = "8"
_repo_app = "Red Hat Enterprise Linux 8 for x86_64 - AppStream (RPMs)"
_release_app = "8"
_repo_tools = "Red Hat Satellite Client 6 for RHEL 8 x86_64 (RPMs)"
_release_tools = "8"

_repo_name_base = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS RPMs 8"
_repo_name_app = "Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 8 x86_64 RPMs"

_environment = "Development/Base"

labname = 'software-modules'


class SoftwareModules(GuidedExercise):
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

            courselib.create_org(_targets, _orgname, _orgdesc),
            courselib.create_loc(_targets, _locname, _orgname),

            courselib.set_default(_orgname, _locname),

            steps.run_command(label="Copy manifest",
                              hosts=["localhost"],
                              command="scp " + _manifest_loc
                              + " root@satellite:" + _manifest,
                              returns="0",
                              shell=True
                              ),
            courselib.check_manifest(_targets, _orgname, _manifest),

            courselib.check_repo(_targets, _repo_base, _orgname, _release_base),
            courselib.check_repo(_targets, _repo_app, _orgname, _release_app),
            courselib.check_repo(_targets, _repo_tools, _orgname, _release_tools),

            courselib.sync_repo(_targets, _orgname, _repo_name_base, _productname),
            courselib.sync_repo(_targets, _orgname, _repo_name_app, _productname),
            courselib.sync_repo(_targets, _orgname, _repo_name_tools, _productname),

            courselib.check_lifecycle(_targets, _orgname, _devlc, _devdesc, _liblc),
            courselib.check_lifecycle(_targets, _orgname, _qalc, _qadesc, _devlc),
            courselib.check_lifecycle(_targets, _orgname, _prodlc, _proddesc, _qalc),

            courselib.create_cv(_targets, _orgname, _cvbase, _cvbasedesc),
            courselib.addrepo_cv(_targets, _orgname, _cvbase, _repo_name_base),
            courselib.addrepo_cv(_targets, _orgname, _cvbase, _repo_name_app),
            courselib.addrepo_cv(_targets, _orgname, _cvbase, _repo_name_tools),

            courselib.content_publish(_orgname, _cvbase, 'Base Repositories', _liblc),
            courselib.promote_cv(_orgname, _cvbase, 'Base Repositories', _devlc),
            courselib.promote_cv(_orgname, _cvbase, 'Base Repositories v2', _qalc),

            courselib.register_host(["serverd"], _orgname, _environment, "--username='admin' --password='redhat'"),

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
            courselib.remove_host(_orgname, "serverd.lab.example.com"),
            courselib.unregister_host(["serverd"]),

            courselib.remove_lifecycle(_targets, _orgname, _prodlc),
            courselib.remove_lifecycle(_targets, _orgname, _qalc),
            courselib.remove_lifecycle(_targets, _orgname, _devlc),
            courselib.remove_lifecycle_env(_targets, _orgname, _cvbase, "Library"),
            courselib.remove_cv(_targets, _orgname, _cvbase),
        ]
        Console(items).run_items(action="Finishing")
