#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Apr 05 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Jun 08 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Dec 27 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 clients.
This module implements the start and finish functions for the
Automate Registration of Content Hosts guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "serverc"]
_client_host_mkt = ["serverc"]

_orgname_ops = "Operations"
_orgname_mkt = "Marketing"
_orgdesc_mkt = "Marketing Department"
_location = "Boston"

_collection = "OpsServers"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_liblc = "Library"
_devlc = "Development"
_devdesc = "Development"
_qalc = "QA"
_qadesc = "Quality Assurance"
_prodlc = "Production"
_proddesc = "Production"

_ops_cv = "OperationsServerBase"
_ops_cv_desc = "Base Packages"
_mkt_cv = "MarketingServerBase"
_mkt_cv_desc = "Marketing Base Packages"
_mkt_env = "Development/MarketingServerBase"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

_ops_activation_key = "OperationsServers"

labname = 'clients-automate'

# Change the class name to match your file name.


class ClientsAutomate(GuidedExercise):
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

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),

            newcourselib.check_location(_location, _orgname_ops),
            newcourselib.check_default_org_loc(_orgname_ops, _location),

            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),

            newcourselib.check_organization(_orgname_mkt, _orgdesc_mkt),

            newcourselib.check_lifecycle(_orgname_mkt, _devlc, _devdesc, _liblc),

            newcourselib.check_cv(_orgname_mkt, _mkt_cv, _mkt_cv_desc),
            newcourselib.check_publish_cv(_orgname_mkt, _mkt_cv, _mkt_cv_desc, _liblc),
            newcourselib.check_promote_cv(_orgname_mkt, _mkt_cv, _mkt_cv_desc, _devlc),

            # newcourselib.register_host(_client_host_mkt, _orgname_mkt, _mkt_env),
            steps.run_command(label=f"Check register '{_client_host_mkt}' client in '{_orgname_mkt}'",
                              hosts=["serverc"],
                              command="if [[ $(subscription-manager status | grep 'Overall Status: Current') ]];"
                                    + " then exit 0;"
                                    + " else subscription-manager clean;"
                                    + " yum -y localinstall http://satellite.lab.example.com/pub/katello-ca-consumer-latest.noarch.rpm;"
                                    + " subscription-manager register --org='" + _orgname_mkt + "'"
                                    + " --environment='" + _mkt_env + "'"
                                    + " --username='admin' --password='redhat'" + "; exit 0; fi",
                              returns=0,
                              shell=True,
                              ),

            newcourselib.check_collection(_orgname_ops, _collection),

            newcourselib.check_lifecycle(_orgname_ops, _devlc, _devdesc, _liblc),
            newcourselib.check_lifecycle(_orgname_ops, _qalc, _qadesc, _devlc),
            newcourselib.check_lifecycle(_orgname_ops, _prodlc, _proddesc, _qalc),

            newcourselib.check_cv(_orgname_ops, _ops_cv, _ops_cv_desc),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_tools),
            newcourselib.check_publish_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _liblc),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _devlc),

            newcourselib.remove_activation_key(_orgname_ops, _ops_activation_key),
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
