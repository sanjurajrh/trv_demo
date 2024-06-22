#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jul 08 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - original code
# * Mar 02 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps


"""
Lab script for RH403 compreview.
This module implements the start and finish functions for the
Compreview Remote Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "serverb"]
_satellite_host = ["satellite"]
_serverb_host = ["serverb"]
_serverb_fqdn = "serverb.lab.example.com"

_orgname = "Finance"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"

_ansibleplaybook_name = "playbook-example-cr.yml"
_ansibleplaybook_loc = _basedir + _ansibleplaybook_name
_to_host = "workstation"
_dest = "/home/student/"

_lclib = "Library"
_lcbuild = "Build"
_lcbuilddesc = "Build"
_lctest = "Test"
_lctestdesc = "Test"
_lcdeploy = "Deploy"
_lcdeploydesc = "Deploy"

_cvname = "FinanceServerBase"
_cvdesc = "FinanceServerBase Repositories"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

_keyname = "FinanceServers"
_keyoptions = "--unlimited-hosts --release-version 9"

_jobtemplate = "Custom banner"


labname = 'compreview-remote'

# Change the class name to match your file name.


class CompreviewRemote(GuidedExercise):
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

            newcourselib.check_sync_product_repos(_orgname, _productname),
            newcourselib.verify_repository(_orgname, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname, _repo_name_app, _productname),
            newcourselib.check_repo_added(_repo_tools, _orgname, _release),
            newcourselib.check_sync_repo(_orgname, _repo_name_tools, _productname),

            newcourselib.check_lifecycle(_orgname, _lcbuild, _lcbuilddesc, _lclib),
            newcourselib.check_lifecycle(_orgname, _lctest, _lctestdesc, _lcbuild),
            newcourselib.check_lifecycle(_orgname, _lcdeploy, _lcdeploydesc, _lctest),

            newcourselib.check_cv(_orgname, _cvname, _cvdesc),
            newcourselib.check_repo_cv(_orgname, _cvname, _repo_name_base),
            newcourselib.check_repo_cv(_orgname, _cvname, _repo_name_app),
            newcourselib.check_repo_cv(_orgname, _cvname, _repo_name_tools),
            newcourselib.check_publish_cv(_orgname, _cvname, _cvdesc, _lclib),
            newcourselib.check_promote_cv(_orgname, _cvname, _cvdesc, _lcbuild),

            newcourselib.check_activation_key(_orgname, _cvname, _lcbuild, _keyname, _keyoptions),

            newcourselib.copy_file(_to_host, _ansibleplaybook_loc, _dest),
            newcourselib.check_root_ssh_login(_serverb_host),

            newcourselib.remove_job_template(_jobtemplate),
            newcourselib.unregister_host(_serverb_host),
            newcourselib.remove_host(_orgname, _serverb_fqdn),
            newcourselib.remove_ssh_banner(_serverb_host),
            newcourselib.remove_foreman_key(_satellite_host, _serverb_host),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label=f"Check if the consumer RPM package is installed in '{_serverb_host[0]}'",
                              hosts=_serverb_host,
                              command="yum list installed"
                                      + " katello-ca-consumer-satellite.lab.example.com",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label=f"Check if the '{_serverb_host[0]}' is registered in Satellite",
                              hosts=_satellite_host,
                              command="hammer host list | grep " + _serverb_fqdn,
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label=f"Check SSH key in '{_serverb_host[0]}'",
                              hosts=_serverb_host,
                              command="grep satellite.lab.example .ssh/authorized_keys",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label=f"Check if '{_jobtemplate}' Ansible job template is present",
                              hosts=_satellite_host,
                              command="hammer job-template list |"
                              + " grep '" + _jobtemplate + "'",
                              returns="0",
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
            newcourselib.remove_root_ssh_login(_serverb_host),
        ]
        Console(items).run_items(action="Finishing")
