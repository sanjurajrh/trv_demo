#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Apr 16 2022 Victor Costea <vcostea@redhat.com>
#   - original code
# * Jun 08 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Dec 27 2022 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps
# * Feb 08 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Remove Base and Apps repos in Marketing
#   - Update to use the correct content view names

"""
Lab script for RH403 clients.
This module implements the start, grade and finish functions for the
Register Hosts review lab.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "serverb"]
_host = ["satellite"]
_hosts = ["serverb"]
_fqdn_serverb = "serverb.lab.example.com"

_orgname_fin = "Finance"

_productname = "Red Hat Enterprise Linux for x86_64"
_release = "9"

_repo_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS (RPMs)"
_repo_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream (RPMs)"
_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"

_lclib = "Library"
_lcbuild = "Build"
_lcbuilddesc = "Build"
_lctest = "Test"
_lctestdesc = "Test"
_lcdeploy = "Deploy"
_lcdeploydesc = "Deploy"

_fin_cv = "FinanceServerBase"
_fin_cv_desc = "Finance Base Packages"

_collection = "FinanceServers"
_fin_activation_key = "FinanceServers"

labname = 'clients-review'

# Change the class name to match your file name.


class ClientsReview(GuidedExercise):
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

            newcourselib.remove_collection(_orgname_fin, _collection),
            newcourselib.remove_activation_key(_orgname_fin, _fin_activation_key),
            newcourselib.remove_host(_orgname_fin, _fqdn_serverb),
            newcourselib.unregister_host(_hosts),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label=f"Verify '{_collection}' host collection",
                              hosts=_host,
                              command="hammer"
                              + " host-collection list "
                              + " --organization " + _orgname_fin
                              + " | grep '" + _collection + "'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label=f"Verify '{_fin_activation_key}' activation key",
                              hosts=_host,
                              command="hammer"
                              + " activation-key list "
                              + " --organization " + _orgname_fin
                              + " | grep '" + _fin_activation_key + "'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label=f"Verify lifecycle for '{_fin_activation_key}' activation key",
                              hosts=_host,
                              command="hammer"
                              + " activation-key info "
                              + " --organization " + _orgname_fin
                              + " --name='" + _fin_activation_key + "' "
                              + " --fields='Lifecycle environment' "
                              + " | grep 'Build'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label=f"Verify content view for '{_fin_activation_key}' activation key",
                              hosts=_host,
                              command="hammer"
                              + " activation-key info "
                              + " --organization " + _orgname_fin
                              + " --name='" + _fin_activation_key + "' "
                              + " --fields='Content View' "
                              + " | grep '" + _fin_cv + "'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify serverb registration",
                              hosts=_host,
                              command="hammer"
                              + " host list "
                              + " --organization " + _orgname_fin
                              + " | grep " + _fqdn_serverb
                              + " ",
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
