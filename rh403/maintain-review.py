#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Aug 11 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Sep 13 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - fix issue setting back default policy
# * Feb 10 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps


"""
Lab script for RH403 Maintain a Satellite Server.
This module implements the start, grade and finish functions for the
Maintain a Red Hat Satellite Server review lab.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite"]
_host = ["satellite"]

_orgname = "Finance"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

_lclib = "Library"
_lcbuild = "Build"
_lcbuilddesc = "Build"
_lctest = "Test"
_lctestdesc = "Testing"
_lcdeploy = "Deploy"
_lcdeploydesc = "Deploy"

_cv = "FinanceServerBase"
_cv_desc = "Base Packages"

_environment = "Build/FinanceServerBase"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/maintain-review/"
_script = "check_cv_versions.sh"

_user = "auditor"
_role = "Compliance Auditor"
_exports = "/var/lib/pulp/exports/*"
_download_policy = "on_demand"


labname = 'maintain-review'


class MaintainReview(GuidedExercise):
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

            newcourselib.check_cv(_orgname, _cv, _cv_desc),
            newcourselib.check_repo_cv(_orgname, _cv, _repo_name_base),
            newcourselib.check_publish_cv(_orgname, _cv, _cv_desc, _lclib),
            newcourselib.check_promote_cv(_orgname, _cv, _cv_desc, _lcbuild),
            newcourselib.check_file_in_satellite(_basedir, _script),
            newcourselib.check_script(_host, _script),

            newcourselib.remove_user(_user),
            newcourselib.remove_role(_role),
            newcourselib.remove_file_directory(_host, _exports),
            newcourselib.check_download_policy(_orgname, _repo_name_base, _download_policy),
            newcourselib.check_download_policy(_orgname, _repo_name_tools, _download_policy),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label=f"Check '{_user}' user",
                              hosts=_targets,
                              command="hammer user info --login "
                                      + _user,
                              returns="0",
                              student_msg="User not found.",
                              shell=True
                              ),
            steps.run_command(label=f"Check '{_role}' role",
                              hosts=_targets,
                              command="hammer role info --name '"
                                      + _role + "'",
                              returns="0",
                              student_msg="Role not found.",
                              shell=True
                              ),
            steps.run_command(label="Check role assigned to user",
                              hosts=_targets,
                              command="hammer user info"
                                      + " --login " + _user
                                      + " --fields Roles |"
                                      + " grep '" + _role + "'",
                              returns="0",
                              student_msg="Role not found in user.",
                              shell=True
                              ),
            steps.run_command(label="Check BaseOS repository download policy",
                              hosts=_targets,
                              command="hammer repository info"
                              + " --organization '" + _orgname + "'"
                              + " --id"
                              + " $(hammer --no-headers repository list "
                              + " --organization '" + _orgname + "'"
                              + " --product '" + _productname + "'"
                              + " --name '" + _repo_name_base + "' --fields Id)"
                              + " --fields 'Download policy' | grep immediate",
                              returns="0",
                              student_msg="Download policy not set.",
                              shell=True
                              ),
            steps.run_command(label="Check Satellite Client repository download policy",
                              hosts=_targets,
                              command="hammer repository info"
                              + " --organization '" + _orgname + "'"
                              + " --id"
                              + " $(hammer --no-headers repository list "
                              + " --organization '" + _orgname + "'"
                              + " --product '" + _productname + "'"
                              + " --name '" + _repo_name_tools + "' --fields Id)"
                              + " --fields 'Download policy' | grep immediate",
                              returns="0",
                              student_msg="Download policy not set.",
                              shell=True
                              ),
            steps.run_command(label="Check Satellite export content",
                              hosts=_targets,
                              command="ls -lR  /var/lib/pulp/exports/Finance/FinanceServerBase/ | grep -E 'export-|metadata'",
                              returns="0",
                              student_msg="Export content not found.",
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
