#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * May 18 2022 Alex Callejas <acalleja@redhat.com>
#   - original code
# * Jun 10 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Dec 30 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps
# * Jan 24 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Using serverd instead serverc
# * Feb 21 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Update CV versions


"""
Lab script for RH403 deploy software.
This module implements the start, grade and finish functions for the
Deploy Software review lab.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise


_targets = ["satellite", "serverb", "serverd"]
_host = ["satellite"]
_host_clientb = ["serverb"]
_fqdn_clientb = "serverb.lab.example.com"
_fqdn_clientd = "serverd.lab.example.com"

_orgname_fin = "Finance"

_lclib = "Library"
_lcbuild = "Build"
_lcbuilddesc = "Build"
_lctest = "Test"
_lctestdesc = "Test"
_lcdeploy = "Deploy"
_lcdeploydesc = "Deploy"

_fin_cv = "FinanceServerBase"
_fin_cv_desc = "Base Packages"
_fin_cv_compose = "BaseHAComposite"
_fin_cv_baseha = "FinBaseHA"
_fin_cv_baseha_filter = "Pacemaker-before-2.1.4"
_fin_cv_base_filter = "Non-security Errata"

_environment = "Build/FinanceServerBase"

_packages = "ant"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_repo_name_ha = "Red Hat Enterprise Linux 9 for x86_64 - High Availability (RPMs)"
_productname = "Red Hat Enterprise Linux for x86_64"


labname = 'software-review'


class SoftwareReview(GuidedExercise):
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

            newcourselib.check_sync_product_repos(_orgname_fin, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_app, _productname),
            newcourselib.check_repo_added(_repo_tools, _orgname_fin, _release),
            newcourselib.check_sync_repo(_orgname_fin, _repo_name_tools, _productname),

            newcourselib.check_lifecycle(_orgname_fin, _lcbuild, _lcbuilddesc, _lclib),
            newcourselib.check_lifecycle(_orgname_fin, _lctest, _lctestdesc, _lcbuild),
            newcourselib.check_lifecycle(_orgname_fin, _lcdeploy, _lcdeploydesc, _lctest),

            newcourselib.check_cv(_orgname_fin, _fin_cv, _fin_cv_desc),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_base),
            newcourselib.check_publish_cv(_orgname_fin, _fin_cv, _fin_cv_desc, _lclib),
            newcourselib.check_promote_cv(_orgname_fin, _fin_cv, _fin_cv_desc, _lcbuild),

            newcourselib.check_host_cv(_orgname_fin, _fin_cv, _lcbuild, _fqdn_clientb),
            newcourselib.register_host(_host_clientb, _orgname_fin, _environment),

            newcourselib.remove_packages(_host_clientb, _packages),
            newcourselib.disable_repo(_orgname_fin, _repo_name_ha, _release),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label="Check Content View " + _fin_cv,
                              hosts=["satellite"],
                              command="if [[ $(hammer content-view info "
                              + "--name "
                              + _fin_cv
                              + " --organization "
                              + _orgname_fin
                              + ") ]]; then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check Composite Content View " + _fin_cv_compose,
                              hosts=["satellite"],
                              command="if [[ $(hammer content-view info "
                              + "--name "
                              + _fin_cv_compose
                              + " --organization "
                              + _orgname_fin
                              + ") ]]; then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check if the ant package is installed",
                              hosts=["serverb"],
                              command="yum list installed ant",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check lifecycle environment on " + _fqdn_clientb,
                              hosts=["satellite"],
                              command="if [[ $(hammer host info"
                              + " --name='" + _fqdn_clientb + "'"
                              + " --organization='" + _orgname_fin + "'"
                              + " --fields='Content information/lifecycle environment/name'"
                              + " | grep " + _lctest
                              + ") ]]; then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label=f"Check '{_fin_cv_base_filter}' filter",
                              hosts=["satellite"],
                              command="if [[ $(hammer content-view filter list"
                              + " --content-view='" + _fin_cv + "'"
                              + " --organization " + _orgname_fin
                              + " | grep '" + _fin_cv_base_filter + "'"
                              + ") ]]; then exit 0; fi",
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
            newcourselib.remove_filter_cv(_orgname_fin, _fin_cv, _fin_cv_base_filter),
            newcourselib.remove_filter_cv(_orgname_fin, _fin_cv_baseha, _fin_cv_baseha_filter),
            steps.run_command(label=f"Check publish '{_fin_cv}' content view in '{_orgname_fin}' organization",
                              hosts=["satellite"],
                              command="if [[ $(hammer --no-headers content-view version info"
                                      + " --content-view='" + _fin_cv + "'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --version $(hammer --no-headers content-view version list"
                                      + " --content-view='" + _fin_cv + "'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --fields Version | head -n1)"
                                      + " --fields Description | grep 'No filter') ]];"
                                      + " then exit 0;"
                                      + " else hammer content-view publish"
                                      + " --name='" + _fin_cv + "'"
                                      + " --description='No filter'"
                                      + " --organization='" + _orgname_fin + "'; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label=f"Check content promotion in '{_lcbuild}' lifecycle environment",
                              hosts=["satellite"],
                              command="hammer content-view version promote"
                                      + " --content-view='" + _fin_cv + "'"
                                      + " --to-lifecycle-environment='" + _lcbuild + "'"
                                      + " --description='No filter'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --version $(hammer --no-headers content-view version list"
                                      + " --content-view='" + _fin_cv + "'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --fields Version | head -n1)",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label=f"Check content promotion in '{_lctest}' lifecycle environment",
                              hosts=["satellite"],
                              command="hammer content-view version promote"
                                      + " --content-view='" + _fin_cv + "'"
                                      + " --to-lifecycle-environment='" + _lctest + "'"
                                      + " --description='No filter'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --version $(hammer --no-headers content-view version list"
                                      + " --content-view='" + _fin_cv + "'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --fields Version | head -n1)",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label=f"Check publish '{_fin_cv_baseha}' content view in '{_orgname_fin}' organization",
                              hosts=["satellite"],
                              command="if [[ $(hammer --no-headers content-view version info"
                                      + " --content-view='" + _fin_cv_baseha + "'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --version $(hammer --no-headers content-view version list"
                                      + " --content-view='" + _fin_cv_baseha + "'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --fields Version | head -n1)"
                                      + " --fields Description | grep 'No filter') ]];"
                                      + " then exit 0;"
                                      + " else hammer content-view publish"
                                      + " --name='" + _fin_cv_baseha + "'"
                                      + " --description='No filter'"
                                      + " --organization='" + _orgname_fin + "'; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label=f"Check content promotion in '{_lcbuild}' lifecycle environment",
                              hosts=["satellite"],
                              command="hammer content-view version promote"
                                      + " --content-view='" + _fin_cv_baseha + "'"
                                      + " --to-lifecycle-environment='" + _lcbuild + "'"
                                      + " --description='No filter'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --version $(hammer --no-headers content-view version list"
                                      + " --content-view='" + _fin_cv_baseha + "'"
                                      + " --organization='" + _orgname_fin + "'"
                                      + " --fields Version | head -n1)",
                              returns="0",
                              shell=True
                              ),
            # steps.run_command(label=f"Check publish '{_fin_cv_compose}' content view in '{_orgname_fin}' organization",
            #                   hosts=["satellite"],
            #                   command="if [[ $(hammer --no-headers content-view version info"
            #                           + " --content-view='" + _fin_cv_compose + "'"
            #                           + " --organization='" + _orgname_fin + "'"
            #                           + " --version $(hammer --no-headers content-view version list"
            #                           + " --content-view='" + _fin_cv_compose + "'"
            #                           + " --organization='" + _orgname_fin + "'"
            #                           + " --fields Version | head -n1)"
            #                           + " --fields Description | grep 'No filter') ]];"
            #                           + " then exit 0;"
            #                           + " else hammer content-view publish"
            #                           + " --name='" + _fin_cv_compose + "'"
            #                           + " --description='No filter'"
            #                           + " --organization='" + _orgname_fin + "'; fi",
            #                   returns="0",
            #                   shell=True
            #                   ),
            # steps.run_command(label=f"Check content promotion in '{_lcbuild}' lifecycle environment",
            #                   hosts=["satellite"],
            #                   command="hammer content-view version promote"
            #                           + " --content-view='" + _fin_cv_compose + "'"
            #                           + " --to-lifecycle-environment='" + _lcbuild + "'"
            #                           + " --description='No filter'"
            #                           + " --organization='" + _orgname_fin + "'"
            #                           + " --version $(hammer --no-headers content-view version list"
            #                           + " --content-view='" + _fin_cv_compose + "'"
            #                           + " --organization='" + _orgname_fin + "'"
            #                           + " --fields Version | head -n1)",
            #                   returns="0",
            #                   shell=True
            #                   ),
            # steps.run_command(label=f"Check content promotion in '{_lctest}' lifecycle environment",
            #                   hosts=["satellite"],
            #                   command="hammer content-view version promote"
            #                           + " --content-view='" + _fin_cv_compose + "'"
            #                           + " --to-lifecycle-environment='" + _lctest + "'"
            #                           + " --description='No filter'"
            #                           + " --organization='" + _orgname_fin + "'"
            #                           + " --version $(hammer --no-headers content-view version list"
            #                           + " --content-view='" + _fin_cv_compose + "'"
            #                           + " --organization='" + _orgname_fin + "'"
            #                           + " --fields Version | head -n1)",
            #                   returns="0",
            #                   shell=True
            #                   ),
        ]
        Console(items).run_items(action="Finishing")
