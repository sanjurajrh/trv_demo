#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Mar 28 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Jun 08 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs folder
# * Jul 05 2022 Patrick Gomez <pagomez@redhat.com>
#   - update content for arch review
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Dec 26 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps
# * Jan 18 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Modified check_foreman_key function
#   - update script to use check_foreman_key function

"""
Lab script for RH403 lifecycles.
This module implements the start and finish functions for the
Synchronize Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "servera"]
_host = ["satellite"]
_client = ["servera"]

_orgname_ops = "Operations"
_location = "Boston"

_liblc = "Library"
_devlc = "Development"
_devdesc = "Development"
_qalc = "QA"
_qadesc = "Quality Assurance"
_prodlc = "Production"
_proddesc = "Production"

_ops_cv = "OperationsServerBase"
_ops_cv_desc = "Base Packages"

_environment = "Development/OperationsServerBase"
_host_collection = "OpsServers"
_packages = "redis"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"


labname = 'clients-collections'

# Change the class name to match your file name.


class ClientsCollections(GuidedExercise):
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

            newcourselib.check_lifecycle(_orgname_ops, _devlc, _devdesc, _liblc),
            newcourselib.check_lifecycle(_orgname_ops, _qalc, _qadesc, _devlc),
            newcourselib.check_lifecycle(_orgname_ops, _prodlc, _proddesc, _qalc),

            newcourselib.check_cv(_orgname_ops, _ops_cv, _ops_cv_desc),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_tools),
            newcourselib.check_publish_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _liblc),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _devlc),

            newcourselib.register_host(_client, _orgname_ops, _environment),
            newcourselib.check_foreman_key(_host, _client),

            newcourselib.remove_collection(_orgname_ops, _host_collection),
            newcourselib.remove_packages(_client, _packages),
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
