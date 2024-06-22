#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jul 08 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - original code
# * Jul 15 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update organization and location
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Aug 31 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - force dynolabs build
# * Feb 01 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps


"""
Lab script for RH403 remote.
This module implements the start and finish functions for the
Remote Review Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "serverb", "serverd"]
_host_satellite = ["satellite"]
_host_capsule = ["capsule"]
_host_serverb = ["serverb"]
_host_serverd = ["serverd"]

_orgname = "Finance"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"
_release = "9"

_lclib = "Library"
_lcbuild = "Build"
_lcbuilddesc = "Build"
_lctest = "Test"
_lctestdesc = "Test"
_lcdeploy = "Deploy"
_lcdeploydesc = "Deploy"

_fin_cv = "FinanceServerBase"
_fin_cv_desc = "Base Packages"
_environmentBase = "Test/FinanceServerBase"

_fin_cv_baseha = "FinBaseHA"
_fin_cv_baseha_filter = "Pacemaker-before-2.1.4"
_fin_cv_base_filter = "Non-security Errata"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_role_file = "apache-setup-role.tgz"
_role_loc = _basedir + _role_file
_to_host = "satellite"
_dest = "/root/"

_packages = "httpd mod_wsgi"
_index_file = "/var/www/html/index.html"
_web_port = "80/tcp"
_apache_file = "/root/apache-setup-role*"
_role_variable = "apache_test_message"
_role_variable_message = "Satellite set this variable"
_role_name = "apache-setup-role"

# >>>>> Capsule variables
_capsule_location = "Boston"

_capsule_fqdn = "capsule.lab.example.com"

_orgname_ops = "Operations"
_cvdefault = "Default Organization View"

_repo_name_base_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS RPMs 8"
_repo_name_app_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8"
_repo_name_maintenance_rhel8 = "Red Hat Satellite Maintenance 6.11 for RHEL 8 x86_64 RPMs"
_repo_name_client_rhel8 = "Red Hat Satellite Client 6 for RHEL 8 x86_64 RPMs"

_repo_capsule_rhel8 = "Red Hat Satellite Capsule 6.11 for RHEL 8 x86_64 (RPMs)"
_repo_maintenance_rhel8 = "Red Hat Satellite Maintenance 6.11 for RHEL 8 x86_64 (RPMs)"
_repo_client_rhel8 = "Red Hat Satellite Client 6 for RHEL 8 x86_64 (RPMs)"
_release_rhel8 = "8"

_repo_name_capsule_rhel8 = "Red Hat Satellite Capsule 6.11 for RHEL 8 x86_64 RPMs"
_productname_capsule = "Red Hat Satellite Capsule"

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
_capsule_packages = "satellite-capsule"
# <<<<< END Capsule variables


labname = 'remote-review'


class RemoteReview(GuidedExercise):
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
            newcourselib.check_location(_capsule_location, _orgname_ops),

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

            newcourselib.check_sync_product_repos(_orgname, _productname),
            newcourselib.verify_repository(_orgname, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname, _repo_name_app, _productname),
            newcourselib.check_repo_added(_repo_tools, _orgname, _release),
            newcourselib.check_sync_repo(_orgname, _repo_name_tools, _productname),

            newcourselib.check_lifecycle(_orgname, _lcbuild, _lcbuilddesc, _lclib),
            newcourselib.check_lifecycle(_orgname, _lctest, _lctestdesc, _lcbuild),
            newcourselib.check_lifecycle(_orgname, _lcdeploy, _lcdeploydesc, _lctest),

            newcourselib.check_cv(_orgname, _fin_cv, _fin_cv_desc),
            newcourselib.check_repo_cv(_orgname, _fin_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname, _fin_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname, _fin_cv, _repo_name_tools),

            newcourselib.check_publish_cv(_orgname, _fin_cv, _fin_cv_desc, _lclib),
            newcourselib.check_promote_cv(_orgname, _fin_cv, _fin_cv_desc, _lcbuild),
            newcourselib.check_promote_cv(_orgname, _fin_cv, _fin_cv_desc, _lctest),

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
            newcourselib.check_packages(_host_capsule, _capsule_packages),
            newcourselib.check_capsule_certs(_capsule_fqdn),
            newcourselib.check_capsule_install(),
            newcourselib.check_capsule_org_loc(_capsule_fqdn, _orgname_ops, _capsule_location),

            newcourselib.register_host(_host_serverb, _orgname, _environmentBase),
            newcourselib.register_host(_host_serverd, _orgname, _environmentBase),
            newcourselib.check_root_ssh_login(_host_serverb),
            newcourselib.check_root_ssh_login(_host_serverd),
            # newcourselib.check_foreman_key(_host_satellite, _host_serverb),
            # newcourselib.check_foreman_key(_host_satellite, _host_serverd),

            newcourselib.remove_foreman_key(_host_satellite, _host_serverb),
            newcourselib.remove_foreman_key(_host_satellite, _host_serverd),
            newcourselib.remove_foreman_key(_host_capsule, _host_serverb),
            newcourselib.remove_foreman_key(_host_capsule, _host_serverd),
            newcourselib.remove_packages(_host_serverb, _packages),
            newcourselib.remove_packages(_host_serverd, _packages),
            newcourselib.remove_file_directory(_host_serverb, _index_file),
            newcourselib.remove_file_directory(_host_serverd, _index_file),
            newcourselib.remove_ports(_host_serverb, _web_port),
            newcourselib.remove_ports(_host_serverd, _web_port),
            newcourselib.remove_file_directory(_host_satellite, _apache_file),
            newcourselib.remove_ansible_variable(_orgname, _role_variable),
            newcourselib.remove_ansible_role(_orgname, _role_name),

            newcourselib.remove_filter_cv(_orgname, _fin_cv, _fin_cv_base_filter),
            newcourselib.remove_filter_cv(_orgname, _fin_cv_baseha, _fin_cv_baseha_filter),

            newcourselib.copy_file(_to_host, _role_loc, _dest),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label="Check SSH key in serverb",
                              hosts=["serverb"],
                              command="grep satellite.lab.example .ssh/authorized_keys",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check SSH key in serverd",
                              hosts=["serverd"],
                              command="grep satellite.lab.example .ssh/authorized_keys",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check if Ansible role is placed in /etc/ansible/roles",
                              hosts=_host_satellite,
                              command="if [[ -d /etc/ansible/roles/apache-setup-role ]];"
                              + " then exit 0; else exit 1; fi",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check if Ansible role is imported to Satellite",
                              hosts=_host_satellite,
                              command="hammer ansible roles list |"
                              + " grep " + _role_name,
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check if Ansible variable is correctly set",
                              hosts=_host_satellite,
                              command="hammer ansible variables list "
                              + " | grep " + _role_variable
                              + " | grep '" + _role_variable_message + "'",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check if Apache server has been successfully deployed on serverb",
                              hosts=["localhost"],
                              command="curl serverb.lab.example.com "
                              + " | grep '" + _role_variable_message + "'",
                              returns="0",
                              shell=True
                              ),
            steps.run_command(label="Check if Apache server has been successfully deployed on serverd",
                              hosts=["localhost"],
                              command="curl serverd.lab.example.com "
                              + " | grep '" + _role_variable_message + "'",
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
            newcourselib.remove_root_ssh_login(_host_serverb),
            newcourselib.remove_root_ssh_login(_host_serverd),
        ]
        Console(items).run_items(action="Finishing")
