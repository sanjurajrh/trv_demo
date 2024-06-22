#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jun 01 2022 Alex Callejas <acalleja@redhat.com>
#   - original code
# * Jun 21 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Aug 04 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - script enhances
# * Sep 07 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - add RPM sign
# * Jan 09 2023 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps


"""
Lab script for RH403 custom admin.
This module implements the start and finish functions for the
Custom Admin Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

# Vars

_targets = ["satellite", "servera"]
_host = ["satellite"]
_host_clienta = ["servera"]
_host_local = ["localhost"]
_fqdn_servera = "servera.lab.example.com"
_orgname_ops = "Operations"
_location = "Boston"
_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"

_productname = "Red Hat Enterprise Linux for x86_64"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_ops_cv = "OperationsServerBase"
_ops_cv_desc = "Base Packages"

_basedir2 = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/custom-admin/"
_script = "check_cv_custom.sh"

_liblc = "Library"
_devlc = "Development"
_devdesc = "Development"
_qalc = "QA"
_qadesc = "Quality Assurance"
_prodlc = "Production"
_proddesc = "Production"

_credname = "Example Software"

_prod_name = "Custom Software"
_repo_name = "Admin Tools"
_pkg1_name = "sm-practice-1.0-1.el9.x86_64.rpm"
_pkg1_loc = _basedir + _pkg1_name

_pkg2_name = "sm-practice"

_pkg3_name = "rpm-sign"

_environment = "Development/OperationsServerBase"

labname = 'custom-admin'


class CustomAdmin(GuidedExercise):
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
            newcourselib.check_location(_location, _orgname_ops),
            newcourselib.check_default_org_loc(_orgname_ops, _location),

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_base, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_app, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),
            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release),

            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),
            newcourselib.check_lifecycle(_orgname_ops, _devlc, _devdesc, _liblc),
            newcourselib.check_lifecycle(_orgname_ops, _qalc, _qadesc, _devlc),
            newcourselib.check_lifecycle(_orgname_ops, _prodlc, _proddesc, _qalc),

            newcourselib.remove_content_credential(_orgname_ops, _credname),

            newcourselib.check_file_in_satellite(_basedir2, _script),
            newcourselib.check_script(_host, _script),

            steps.run_command(label=f"Removing product '{_prod_name}'",
                              hosts=_targets,
                              command="if [[ $(hammer product list"
                              + " --organization " + _orgname_ops
                              + " | grep '" + _prod_name + "') ]];"
                              + " then hammer product delete"
                              + " --name='" + _prod_name + "'"
                              + " --organization='" + _orgname_ops + "';"
                              + " exit 0; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label=f"Unregister '{_host_clienta}'",
                              hosts=["servera"],
                              command="if [[ $(subscription-manager status | grep 'Overall Status: Unknown') ]];"
                              + " then exit 0;"
                              + " else  subscription-manager unregister;"
                              + " subscription-manager clean;"
                              + " yum -y remove katello-ca-consumer-satellite.lab.example.com.noarch;"
                              + " yum clean all; exit 0; fi",
                              returns="0",
                              shell=True
                              ),

            newcourselib.check_cv(_orgname_ops, _ops_cv, _ops_cv_desc),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_tools),
            newcourselib.check_publish_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _liblc),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _devlc),

            steps.run_command(label=f"Creating custom product in {_orgname_ops}",
                              hosts=["satellite"],
                              command="if [[ $(hammer --no-headers product list"
                              + " --organization='" + _orgname_ops + "'"
                              + " | grep '" + _prod_name + "' ) ]];"
                              + " then exit 0;"
                              + " else hammer product create"
                              + " --name='" + _prod_name + "'"
                              + " --description='" + _prod_name + "'"
                              + " --organization='" + _orgname_ops + "'; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label=f"Creating repository {_repo_name} in {_orgname_ops}",
                              hosts=["satellite"],
                              command="if [[ $(hammer --no-headers repository list"
                              + " --organization='" + _orgname_ops + "'"
                              + " | grep '" + _repo_name + "' ) ]];"
                              + " then exit 0;"
                              + " else hammer repository create"
                              + " --name='" + _repo_name + "'"
                              + " --product='" + _prod_name + "'"
                              + " --content-type yum"
                              + " --description='" + _prod_name + "'"
                              + " --organization='" + _orgname_ops + "'; fi",
                              returns="0",
                              shell=True
                              ),

            newcourselib.remove_packages(_host_clienta, _pkg2_name),

            steps.run_command(label=f"Verifying the '{_pkg3_name}' package",
                              hosts=["localhost"],
                              command="if [[ $(ssh root@localhost yum list " + _pkg3_name
                              + " --installed) ]];"
                              + " then ssh root@localhost yum -y remove " + _pkg3_name
                              + " ; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Remove rpm file from workstation server",
                              hosts=["localhost"],
                              command="rm -rf "
                              + " /home/student/" + _pkg1_name,
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Remove rpmmacro file from workstation server",
                              hosts=["localhost"],
                              command="rm -rf /home/student/.rpmmacros",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Remove armor file from workstation server",
                              hosts=["localhost"],
                              command="rm -rf /home/student/public_key",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Remove gpg key pair from workstation server",
                              hosts=["localhost"],
                              command="rm -rf /home/student/.gnupg/pubring.kbx",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Copy content to workstation server",
                              hosts=["localhost"],
                              command="cp " + _pkg1_loc
                              + " /home/student/" + _pkg1_name,
                              returns="0",
                              shell=True
                              ),

            newcourselib.register_host(_host_clienta, _orgname_ops, _environment),
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
