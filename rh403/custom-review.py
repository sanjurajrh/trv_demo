#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jun 07 2022 Alex Callejas <acalleja@redhat.com>
#   - original code
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Jan 10 2023 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps


"""
Lab script for RH403 deploy software.
This module implements the start, grade and finish functions for the
Deploy Software review lab.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

# Vars
_targets = ["satellite"]
_host = ["satellite"]
_host_clientb = ["serverb"]
_host_local = ["localhost"]
_fqdn_serverb = "serverb.lab.example.com"
_orgname_fin = "Finance"
_locsf = "San Francisco"
_loct = "Tokyo"
_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"

_productname = "Red Hat Enterprise Linux for x86_64"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_fin_cv = "FinanceServerBase"
_fin_cv_desc = "Base Packages"

_liblc = "Library"
_buildlc = "Build"
_builddesc = "Build"
_testlc = "Test"
_testdesc = "Test"
_deploylc = "Deploy"
_deploydesc = "Deploy"

_environment = "'Build/FinanceServerBase'"

_prod_name = "'Custom Software'"
_repo_name = "'Admin Tools'"

_keyname = "FinanceServers"
_keyoptions = "--unlimited-hosts --release-version 9"

_keyoveroptions_base = ("--content-label rhel-8-for-x86_64-baseos-rpms --value 0")
_keyoveroptions_app = ("--content-label rhel-8-for-x86_64-appstream-rpms --value 0")

_gpgname = "'Example Software'"
_gpgkey = "EXAMPLE-RPM-GPG-KEY"
_gpgkey_loc = _basedir + _gpgkey

_pkg1_name = "bkp-1.0-1.el9.x86_64.rpm"
_pkg1_loc = _basedir + "/custom-review/" + _pkg1_name
_pkg2_name = "bkp"
_pkg3_name = "rpm-sign"

_script = "check_cv_review.sh"
_script_loc = _basedir + "custom-review/"

labname = 'custom-review'


class CustomReview(GuidedExercise):
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
            newcourselib.verify_organization_cdn(_orgname_fin),
            newcourselib.check_location(_locsf, _orgname_fin),
            newcourselib.check_location(_loct, _orgname_fin),
            newcourselib.check_default_org_loc(_orgname_fin, _loct),

            newcourselib.check_sync_product_repos(_orgname_fin, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_app, _productname),
            newcourselib.check_repo_added(_repo_tools, _orgname_fin, _release),
            newcourselib.check_sync_repo(_orgname_fin, _repo_name_tools, _productname),

            newcourselib.check_lifecycle(_orgname_fin, _buildlc, _builddesc, _liblc),
            newcourselib.check_lifecycle(_orgname_fin, _testlc, _testdesc, _buildlc),
            newcourselib.check_lifecycle(_orgname_fin, _deploylc, _deploydesc, _testlc),

            newcourselib.remove_activation_key(_orgname_fin, _keyname),

            newcourselib.check_file_in_satellite(_script_loc, _script),
            newcourselib.check_script(_host, _script),

            newcourselib.remove_repository(_orgname_fin, _repo_name, _prod_name),

            steps.run_command(label=f"Removing product '{_prod_name}'",
                              hosts=_targets,
                              command="if [[ $(hammer product list"
                              + " --organization " + _orgname_fin
                              + " | grep '" + _prod_name + "') ]];"
                              + " then hammer product delete"
                              + " --name='" + _prod_name + "'"
                              + " --organization='" + _orgname_fin + "';"
                              + " exit 0; fi",
                              returns="0",
                              shell=True
                              ),

            newcourselib.remove_content_credential(_orgname_fin, _gpgname),

            steps.run_command(label=f"Unregister '{_host_clientb}'",
                              hosts=["serverb"],
                              command="if [[ $(subscription-manager status | grep 'Overall Status: Unknown') ]];"
                              + " then exit 0;"
                              + " else  subscription-manager unregister;"
                              + " subscription-manager clean;"
                              + " yum -y remove katello-ca-consumer-satellite.lab.example.com.noarch;"
                              + " yum clean all; exit 0; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Remove gpg key pair from workstation server",
                              hosts=["localhost"],
                              command="rm -rf /home/student/" + _gpgkey,
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Remove package from workstation server",
                              hosts=["localhost"],
                              command="rm -rf /home/student/" + _pkg1_name,
                              returns="0",
                              shell=True
                              ),
            newcourselib.remove_packages(_host_clientb, _pkg2_name),

            steps.run_command(label=f"Verifying the '{_pkg3_name}' package",
                              hosts=["localhost"],
                              command="if [[ $(ssh root@localhost yum list " + _pkg3_name
                              + " --installed) ]];"
                              + " then ssh root@localhost yum -y remove " + _pkg3_name
                              + " ; fi",
                              returns="0",
                              shell=True
                              ),

            newcourselib.check_cv(_orgname_fin, _fin_cv, _fin_cv_desc),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_tools),
            newcourselib.check_publish_cv(_orgname_fin, _fin_cv, _fin_cv_desc, _liblc),
            newcourselib.check_promote_cv(_orgname_fin, _fin_cv, _fin_cv_desc, _buildlc),

            newcourselib.check_activation_key(_orgname_fin, _fin_cv, _buildlc, _keyname, _keyoptions),
            newcourselib.check_key_override(_orgname_fin, _keyname, _keyoveroptions_base),
            newcourselib.check_key_override(_orgname_fin, _keyname, _keyoveroptions_app),

            steps.run_command(label="Copy rpm file to workstation server",
                              hosts=["localhost"],
                              command="cp " + _pkg1_loc
                              + " /home/student/" + _pkg1_name,
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Copy gpg key to workstation server",
                              hosts=["localhost"],
                              command="cp " + _gpgkey_loc
                              + " /home/student/" + _gpgkey,
                              returns="0",
                              shell=True
                              ),

            newcourselib.register_host(_host_clientb, _orgname_fin, _environment),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label="Check Product " + _prod_name,
                              hosts=["satellite"],
                              command="if [[ $(hammer product info "
                              + "--name "
                              + _prod_name
                              + " --organization "
                              + _orgname_fin
                              + ") ]]; then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check Repository " + _repo_name,
                              hosts=["satellite"],
                              command="if [[ $(hammer repository info "
                              + " --organization "
                              + _orgname_fin
                              + " --product "
                              + _prod_name
                              + " --name "
                              + _repo_name
                              + ") ]]; then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check GPG key " + _gpgname,
                              hosts=["satellite"],
                              command="if [[ $(hammer content-credentials info "
                              + " --organization "
                              + _orgname_fin
                              + " --name "
                              + _gpgname
                              + ") ]]; then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check software package on serverb",
                              hosts=["serverb"],
                              command="if [[ $(rpm -qa "
                              + " | grep "
                              + _pkg2_name
                              + ") ]]; then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check host registration on serverb",
                              hosts=["serverb"],
                              command="if [[ $(subscription-manager identity "
                              + " | grep "
                              + _orgname_fin
                              + ") ]]; then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check host environment on serverb",
                              hosts=["serverb"],
                              command="if [[ $(subscription-manager identity "
                              + " | grep "
                              + _environment
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
