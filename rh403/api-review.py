#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jul 21 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Sep 22 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - add Ansible content
# * Feb 02 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 api.
This module implements the start and finish functions for the
Manage Red Hat Satellite with the API laboratory exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]
_host_clientd = ["serverd"]
_host_workstation = ["workstation"]
_clientd_fqdn = "serverd.lab.example.com"
_orgname = "Finance"

_lclib = "Library"
_lcbuild = "Build"
_lcbuilddesc = "Build"
_lctest = "Test"
_lctestdesc = "Test"
_lcdeploy = "Deploy"
_lcdeploydesc = "Deploy"

_lc_dev = "Development"
_lc_test = "Testing"

_cv_fin = "FinanceServerBase"
_cv_fin_desc = "Base Packages"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_productname = "Red Hat Enterprise Linux for x86_64"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_ansibletar_name = "redhat-satellite-3.6.0.tgz"
_ansiblecomm_tar = "community-general-7.2.1.tar.gz"
_ansibletar_loc = _basedir + _ansibletar_name
_to_host = "workstation"
_dest = "/home/student/"

_ansible_lab = "/home/student/ansible-lab"
_ansible_collections = "/usr/share/ansible/collections/ansible_collections"

_key_finance = "FinancePlaybook"


labname = 'api-review'

# Change the class name to match your file name.


class ApiReview(GuidedExercise):
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

            newcourselib.copy_file(_to_host, _ansibletar_loc, _dest),
            newcourselib.copy_file(_to_host, _ansiblecomm_tar, _dest),

            newcourselib.check_lifecycle(_orgname, _lcbuild, _lcbuilddesc, _lclib),
            newcourselib.check_lifecycle(_orgname, _lctest, _lctestdesc, _lcbuild),
            newcourselib.check_lifecycle(_orgname, _lcdeploy, _lcdeploydesc, _lctest),

            newcourselib.check_cv(_orgname, _cv_fin, _cv_fin_desc),
            newcourselib.check_repo_cv(_orgname, _cv_fin, _repo_name_base),
            newcourselib.check_repo_cv(_orgname, _cv_fin, _repo_name_app),
            newcourselib.check_publish_cv(_orgname, _cv_fin, _cv_fin_desc, _lclib),
            newcourselib.check_promote_cv(_orgname, _cv_fin, _cv_fin_desc, _lcbuild),

            newcourselib.remove_lifecycle(_orgname, _lc_test),
            newcourselib.remove_lifecycle(_orgname, _lc_dev),
            newcourselib.remove_activation_key(_orgname, _key_finance),
            newcourselib.unregister_host(_host_clientd),
            newcourselib.remove_host(_orgname, _clientd_fqdn),
            newcourselib.remove_file_directory(_host_workstation, _ansible_lab),
            # newcourselib.remove_file_directory(_host_workstation, _ansible_collections),
            steps.run_command(label="Remove ansible_collections directory in workstation",
                              hosts=["localhost"],
                              command=f"ssh root@workstation 'rm -rf {_ansible_collections}'",
                              returns=0,
                              shell=True,
                              ),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label=f"Verify environment path for '{_orgname}' organization",
                              hosts=_targets,
                              command="hammer"
                              + " lifecycle-environment paths "
                              + " --organization '" + _orgname + "'"
                              + " | grep 'Library >> Development >> Testing'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify Satellite Ansible Collection is installed in the shared folder",
                              hosts=["localhost"],
                              command="if [[ -d /usr/share/ansible/collections/ansible_collections/redhat/satellite ]];"
                              + " then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True,
                              ),
            steps.run_command(label=f"Verify '{_key_finance}' activation key",
                              hosts=_targets,
                              command="hammer"
                              + " --output base "
                              + " activation-key list "
                              + " --organization " + _orgname
                              + " | grep '" + _key_finance + "'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label=f"Check host registration on '{_host_clientd[0]}'",
                              hosts=_host_clientd,
                              command="if [[ $(subscription-manager identity "
                              + " | grep "
                              + _orgname
                              + ") ]]; then exit 0; else exit 1; fi",
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
        ]
        Console(items).run_items(action="Finishing")
