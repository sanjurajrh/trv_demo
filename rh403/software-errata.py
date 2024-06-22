#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * May 10 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - original code
# * Jun 10 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - use library
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Dec 30 2022 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps
# * Jan 10 2022 Alex Callejas <acalleja@redhat.com>
#   - Add package version check
# * Feb 21 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Update CV versions

"""
Lab script for RH403 software.
This module implements the start and finish functions for the
Manage and Apply Errata to Hosts guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "servera"]
_host = ["satellite"]
_host_clienta = ["servera"]
_host_clientc = ["serverc"]
_host_clienta_fqdn = "servera.lab.example.com"
_host_clientc_fqdn = "serverc.lab.example.com"

_orgname_ops = "Operations"
_location = "Boston"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

_repo_ha = "Red Hat Enterprise Linux 9 for x86_64 - High Availability (RPMs)"
_repo_name_ha = "Red Hat Enterprise Linux 9 for x86_64 - High Availability RPMs 9"
_productname_ha = "Red Hat Enterprise Linux High Availability for x86_64"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_keyname = "OperationsServers"
_dev_env = "Development/OperationsServerBase"
_env_dev_com = "Development/BaseHAComposite"
_ops_cv = "OperationsServerBase"
_ops_cv_desc = "Base Packages"

_filter_osb = "Non-security Errata"

_ops_cv_baseha = "OpsBaseHA"
_ops_cv_baseha_desc = "HA Repository"
_ops_cv_hacompose = "BaseHAComposite"
_ops_cv_hacompose_desc = "Base and HA Content Views Repositories"

_lclib = "Library"
_lcdev = "Development"
_lcdevdesc = "Development"
_lcqa = "QA"
_lcqadesc = "Quality Assurance"
_lcprod = "Production"
_lcproddesc = "Production"

_pkgs = "vim-minimal vim-common"
_base_url_pkg = "http://materials.lab.example.com/content/rhel9.0/x86_64/dvd/"
_pkg1 = "BaseOS/Packages/vim-minimal-8.2.2637-15.el9.x86_64.rpm"
_pkg2 = "BaseOS/Packages/vim-filesystem-8.2.2637-15.el9.noarch.rpm"
_pkg3 = "AppStream/Packages/vim-common-8.2.2637-15.el9.x86_64.rpm"
_pkg4 = "AppStream/Packages/vim-enhanced-8.2.2637-15.el9.x86_64.rpm"

labname = 'software-errata'

# Change the class name to match your file name.


class SoftwareErrata(GuidedExercise):
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
            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),

            newcourselib.check_repo_added(_repo_ha, _orgname_ops, _release),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_ha, _productname_ha),

            newcourselib.check_lifecycle(_orgname_ops, _lcdev, _lcdevdesc, _lclib),
            newcourselib.check_lifecycle(_orgname_ops, _lcqa, _lcqadesc, _lcdev),
            newcourselib.check_lifecycle(_orgname_ops, _lcprod, _lcproddesc, _lcqa),

            newcourselib.check_cvs_in_place(_orgname_ops, _ops_cv),

            newcourselib.check_cv(_orgname_ops, _ops_cv_baseha, _ops_cv_baseha_desc),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv_baseha, _repo_name_ha),
            newcourselib.check_publish_cv(_orgname_ops, _ops_cv_baseha, _ops_cv_baseha_desc, _lclib),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv_baseha, _ops_cv_baseha_desc, _lcdev),

            newcourselib.check_cv(_orgname_ops, _ops_cv_hacompose, _ops_cv_hacompose_desc, "--composite --auto-publish yes"),
            newcourselib.check_component_cv(_orgname_ops, _ops_cv_hacompose, _ops_cv),
            newcourselib.check_component_cv(_orgname_ops, _ops_cv_hacompose, _ops_cv_baseha),
            newcourselib.check_publish_cv(_orgname_ops, _ops_cv_hacompose, _ops_cv_hacompose_desc, _lclib),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv_hacompose, _ops_cv_hacompose_desc, _lcdev),

            newcourselib.check_host_cv(_orgname_ops, _ops_cv, _lcdev, _host_clienta_fqdn),
            newcourselib.check_host_cv(_orgname_ops, _ops_cv_hacompose, _lcdev, _host_clientc_fqdn),
            newcourselib.register_host(_host_clienta, _orgname_ops, _dev_env),
            newcourselib.register_host(_host_clientc, _orgname_ops, _env_dev_com),

            newcourselib.remove_foreman_key(_host, _host_clienta),
            newcourselib.check_root_ssh_login(_host_clienta),

            steps.run_command(label="Check package version on servera.",
                              hosts=["servera"],
                              command="if [[ $(yum list vim-minimal-8.2.2637-16.el9_0.2.x86_64 --installed) ]];"
                              + " then yum -y remove " + _pkgs
                              + " ; yum -y install " + _base_url_pkg + _pkg1
                              + " " + _base_url_pkg + _pkg2
                              + " " + _base_url_pkg + _pkg3
                              + " " + _base_url_pkg + _pkg4
                              + " ; exit 0; fi",
                              returns="0",
                              shell=True
                              ),
        ]
        Console(items).run_items(action="Starting")

    def finish(self):
        """
        Perform any post-lab cleanup tasks.
        """
        items = [
            newcourselib.verify_systems(_targets),
            newcourselib.remove_root_ssh_login(_host_clienta),
            newcourselib.remove_filter_cv(_orgname_ops, _ops_cv, _filter_osb),
            newcourselib.check_cvs_in_place(_orgname_ops, _ops_cv),
        ]
        Console(items).run_items(action="Finishing")
