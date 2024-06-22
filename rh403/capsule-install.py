#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * May 31 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Jun 15 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - use library
# * Jun 27 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - change content to Dynolabs package
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Jan 11 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps


"""
Lab script for RH403 software.
This module implements the start and finish functions for the
Install a Satellite Capsule Server guided exercise.
"""

from . import newcourselib
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "capsule"]
_capsule_host = ["capsule"]
_capsule_fqdn = "capsule.lab.example.com"

_orgname_ops = "Operations"
_location = "Boston"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"
_repo_base_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS (RPMs)"
_repo_app_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - AppStream (RPMs)"

_repo_capsule_rhel8 = "Red Hat Satellite Capsule 6.11 for RHEL 8 x86_64 (RPMs)"
_repo_maintenance_rhel8 = "Red Hat Satellite Maintenance 6.11 for RHEL 8 x86_64 (RPMs)"
_repo_client_rhel8 = "Red Hat Satellite Client 6 for RHEL 8 x86_64 (RPMs)"

_release_rhel8 = "8"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_repo_name_base_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS RPMs 8"
_repo_name_app_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8"
_productname = "Red Hat Enterprise Linux for x86_64"

_lclib = "Library"
_lcdev = "Development"
_lcdevdesc = "Development"
_lcqa = "QA"
_lcqadesc = "Quality Assurance"
_lcprod = "Production"
_lcproddesc = "Production"

_ops_cv = "OperationsServerBase"
_ops_cv_desc = "Base Packages"

_repo_name_capsule_rhel8 = "Red Hat Satellite Capsule 6.11 for RHEL 8 x86_64 RPMs"
_repo_name_maintenance_rhel8 = "Red Hat Satellite Maintenance 6.11 for RHEL 8 x86_64 RPMs"
_repo_name_client_rhel8 = "Red Hat Satellite Client 6 for RHEL 8 x86_64 RPMs"

_keyname = "Capsule"

_packages = "foreman-proxy-content tfm-rubygem-foreman_ansible_core.noarch"
_cert_files = "/root/capsule_cert*"


labname = 'capsule-install'

# Change the class name to match your file name.


class CapsulInstall(GuidedExercise):
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
            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base_rhel8, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app_rhel8, _productname),

            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),

            newcourselib.remove_activation_key(_orgname_ops, _keyname),
            newcourselib.remove_capsule(_capsule_fqdn),
            newcourselib.remove_packages(_capsule_host, _packages),
            newcourselib.remove_file_directory(_targets, _cert_files),
            newcourselib.unregister_host(_capsule_host),
            newcourselib.remove_host(_orgname_ops, _capsule_fqdn),

            newcourselib.check_lifecycle(_orgname_ops, _lcdev, _lcdevdesc, _lclib),
            newcourselib.check_lifecycle(_orgname_ops, _lcqa, _lcqadesc, _lcdev),
            newcourselib.check_lifecycle(_orgname_ops, _lcprod, _lcproddesc, _lcqa),

            newcourselib.check_cv(_orgname_ops, _ops_cv, _ops_cv_desc),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_tools),
            newcourselib.check_publish_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _lclib),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _lcdev),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv, 'Base Repositories v2', _lcqa),

            newcourselib.disable_repo(_orgname_ops, _repo_capsule_rhel8, _release_rhel8),
            newcourselib.disable_repo(_orgname_ops, _repo_maintenance_rhel8, _release_rhel8),
            newcourselib.disable_repo(_orgname_ops, _repo_client_rhel8, _release_rhel8),
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
