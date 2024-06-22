#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Apr 01 2022 Alex Callejas <acalleja@redhat.com>
#   - original code
# * Jun 08 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Jul 06 2022 Alex Callejas <acalleja@redhat.com>
#   - remove activation-key creation
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Dec 26 2022 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 content host register.
This module implements the start and finish functions for the
Synchronize Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

# Vars

_targets = ["satellite", "servera", "serverc"]
_hosts = ["servera", "serverc"]
_fqdn_servera = "servera.lab.example.com"
_fqdn_serverc = "serverc.lab.example.com"

_orgname_ops = "Operations"
_orgname_mkt = "Marketing"
_orgdesc_mkt = "Marketing Department"
_location = "Boston"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_manifest_mkt = "manifest_marketing.zip"

_liblc = "Library"
_devlc = "Development"
_devdesc = "Development"
_qalc = "QA"
_qadesc = "Quality Assurance"
_prodlc = "Production"
_proddesc = "Production"

_cvbase_ops = "OperationsServerBase"
_cvbase_mkt = "MarketingServerBase"
_cvbasedesc = "Base Packages"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"


_repo_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS (RPMs)"
_repo_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream (RPMs)"
_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

labname = 'clients-register'


class ClientsRegister(GuidedExercise):
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

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),

            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),

            newcourselib.check_lifecycle(_orgname_ops, _devlc, _devdesc, _liblc),
            newcourselib.check_lifecycle(_orgname_ops, _qalc, _qadesc, _devlc),
            newcourselib.check_lifecycle(_orgname_ops, _prodlc, _proddesc, _qalc),

            newcourselib.check_cv(_orgname_ops, _cvbase_ops, _cvbasedesc),
            newcourselib.check_repo_cv(_orgname_ops, _cvbase_ops, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_ops, _cvbase_ops, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_ops, _cvbase_ops, _repo_name_tools),

            newcourselib.check_publish_cv(_orgname_ops, _cvbase_ops, _cvbasedesc, _liblc),
            newcourselib.check_promote_cv(_orgname_ops, _cvbase_ops, _cvbasedesc, _devlc),

            newcourselib.check_manifest_in_satellite(_basedir, _manifest_mkt),
            newcourselib.check_organization(_orgname_mkt, _orgdesc_mkt),
            newcourselib.check_manifest(_orgname_mkt, _manifest_mkt),
            newcourselib.verify_organization_cdn(_orgname_mkt),
            newcourselib.check_location(_location, _orgname_mkt),

            newcourselib.check_repo_added(_repo_base, _orgname_mkt, _release),
            newcourselib.check_repo_added(_repo_app, _orgname_mkt, _release),
            newcourselib.check_repo_added(_repo_tools, _orgname_mkt, _release),
            newcourselib.check_sync_repo(_orgname_mkt, _repo_name_base, _productname),
            newcourselib.check_sync_repo(_orgname_mkt, _repo_name_app, _productname),
            newcourselib.check_sync_repo(_orgname_mkt, _repo_name_tools, _productname),

            newcourselib.check_lifecycle(_orgname_mkt, _devlc, _devdesc, _liblc),
            newcourselib.check_lifecycle(_orgname_mkt, _qalc, _qadesc, _devlc),
            newcourselib.check_lifecycle(_orgname_mkt, _prodlc, _proddesc, _qalc),

            newcourselib.check_cv(_orgname_mkt, _cvbase_mkt, _cvbasedesc),
            newcourselib.check_repo_cv(_orgname_mkt, _cvbase_mkt, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_mkt, _cvbase_mkt, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_mkt, _cvbase_mkt, _repo_name_tools),
            newcourselib.check_publish_cv(_orgname_mkt, _cvbase_mkt, _cvbasedesc, _liblc),
            newcourselib.check_promote_cv(_orgname_mkt, _cvbase_mkt, _cvbasedesc, _devlc),

            newcourselib.remove_host(_orgname_ops, _fqdn_servera),
            newcourselib.remove_host(_orgname_mkt, _fqdn_serverc),
            newcourselib.unregister_host(_hosts),
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
