#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jun 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - original code
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Aug 22 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - fix root connection through SSH
# * Nov 10 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Added validation in "Update Capsule organization and location" step
#   - Using "update_capsule_org_loc" function
# * Jan 23 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps


"""
Lab script for RH403 remote.
This module implements the start and finish functions for the
Remote Run Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "capsule", "servera"]
_host_servera = ["servera"]
_host_satellite = ["satellite"]
_host_capsule = ["capsule"]
_capsule_fqdn = "capsule.lab.example.com"

_orgname_ops = "Operations"
_location = "Boston"

_lclib = "Library"
_lcdev = "Development"
_lcdevdesc = "Development"
_lcqa = "QA"
_lcqadesc = "Quality Assurance"
_lcprod = "Production"
_lcproddesc = "Production"

_cvdefault = "Default Organization View"

_ops_cv = "OperationsServerBase"
_ops_cv_desc = "Base Packages"
_environmentBase = "Development/OperationsServerBase"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_repo_name_base_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS RPMs 8"
_repo_name_app_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8"
_repo_name_maintenance_rhel8 = "Red Hat Satellite Maintenance 6.11 for RHEL 8 x86_64 RPMs"
_repo_name_client_rhel8 = "Red Hat Satellite Client 6 for RHEL 8 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

_repo_name_capsule_rhel8 = "Red Hat Satellite Capsule 6.11 for RHEL 8 x86_64 RPMs"
_productname_capsule = "Red Hat Satellite Capsule"

_repo_capsule_rhel8 = "Red Hat Satellite Capsule 6.11 for RHEL 8 x86_64 (RPMs)"
_repo_maintenance_rhel8 = "Red Hat Satellite Maintenance 6.11 for RHEL 8 x86_64 (RPMs)"
_repo_client_rhel8 = "Red Hat Satellite Client 6 for RHEL 8 x86_64 (RPMs)"
_release_rhel8 = "8"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_keyname = "Capsule"
_keyoptions = "--unlimited-hosts --release-version 8 --description 'External Capsule Server'"
_keyoveroptions_base = ("--content-label rhel-8-for-x86_64-baseos-rpms --value 1")
_keyoveroptions_app = ("--content-label rhel-8-for-x86_64-appstream-rpms --value 1")
_keyoveroptions_capsule = ("--content-label satellite-capsule-6.11-for-rhel-8-x86_64-rpms --value 1")
_keyoveroptions_maintenance = ("--content-label satellite-maintenance-6.11-for-rhel-8-x86_64-rpms --value 1")
_keyoveroptions_client = ("--content-label satellite-client-6-for-rhel-8-x86_64-rpms --value 1")

_ports_satellite = "5646/tcp"
_ports_capsule = "53/udp 53/tcp  67/udp 69/udp  80/tcp 443/tcp  5647/tcp  8000/tcp 8140/tcp  8443/tcp 9090/tcp"
_modules = "satellite-capsule:el8"
_packages = "satellite-capsule"


_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_playbook_name = "playbook-example.yml"
_playbook_loc = _basedir + _playbook_name
_dest = "/home/student/"
_from_host = "workstation"

_jobtemplate = "My new custom banner"


labname = 'remote-run'

# Change the class name to match your file name.


class RemoteRun(GuidedExercise):
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
            newcourselib.check_repo_added(_repo_capsule_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_maintenance_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_client_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_capsule_rhel8, _productname_capsule),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_maintenance_rhel8, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_client_rhel8, _productname),

            newcourselib.check_lifecycle(_orgname_ops, _lcdev, _lcdevdesc, _lclib),
            newcourselib.check_lifecycle(_orgname_ops, _lcqa, _lcqadesc, _lcdev),
            newcourselib.check_lifecycle(_orgname_ops, _lcprod, _lcproddesc, _lcqa),
            newcourselib.check_cv(_orgname_ops, _ops_cv, _ops_cv_desc),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_tools),
            newcourselib.check_publish_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _lclib),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _lcdev),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _lcqa),

            newcourselib.check_activation_key(_orgname_ops, _cvdefault, _lclib, _keyname, _keyoptions),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_base),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_app),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_capsule),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_maintenance),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_client),

            newcourselib.check_bootstrap_capsule(_orgname_ops, _keyname),
            newcourselib.check_ports(_host_satellite, _ports_satellite),
            newcourselib.check_ports(_host_capsule, _ports_capsule),
            newcourselib.check_yum_module(_host_capsule, _modules),
            newcourselib.check_packages(_host_capsule, _packages),
            newcourselib.check_capsule_certs(_capsule_fqdn),
            newcourselib.check_capsule_install(),
            newcourselib.check_capsule_org_loc(_capsule_fqdn, _orgname_ops, _location),

            newcourselib.register_host(_host_servera, _orgname_ops, _environmentBase),
            newcourselib.copy_file(_from_host, _playbook_loc, _dest),
            newcourselib.check_root_ssh_login(_host_servera),
            newcourselib.remove_foreman_key(_host_satellite, _host_servera),
            newcourselib.remove_foreman_key(_host_capsule, _host_servera),
            newcourselib.remove_job_template(_jobtemplate),
            newcourselib.remove_ssh_banner(_host_servera),
            steps.run_command(label="Remove servera from known_hosts file",
                              hosts=["capsule"],
                              command="ssh-keygen -R servera",
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
            newcourselib.remove_root_ssh_login(_host_servera),
        ]
        Console(items).run_items(action="Finishing")
