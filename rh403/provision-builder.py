#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Aug 10 2022 Patrick Gomez <pagomez@redhat.com>
#   - original code
# * Mar 10 2023 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for the RH403 course.
This module implements the start and finish functions
for the provision-builder Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "capsule", "servera"]
_satellite_host = ["satellite"]
_capsule_host = ["capsule"]
_capsule_fqdn = "capsule.lab.example.com"
_capsule_client = "capsule"
_servera_client = "servera"
_servera_host = ["servera"]
_servere_fqdn = "servere.boston.lab.example.com"
_orgname_ops = "Operations"
_location = "Boston"


_orgname_fin = "Finance"
_loc_fin = "Tokyo"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/"
_file_loc = _basedir + "provision-builder/rhel-90.json"
_dest = "/root/"

_repo_base_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS (RPMs)"
_repo_app_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - AppStream (RPMs)"
_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"
_release_rhel9 = "9"

_repo_kickstart_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS (Kickstart)"
_repo_kickstart_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream (Kickstart)"
_repo_name_kickstart_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS Kickstart 9.0"
_repo_name_kickstart_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream Kickstart 9.0"
_release_rhel9_kickstart = "9.0"

_repo_name_base_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS RPMs 8"
_repo_name_app_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8"

_repo_capsule_rhel8 = "Red Hat Satellite Capsule 6.11 for RHEL 8 x86_64 (RPMs)"
_repo_maintenance_rhel8 = "Red Hat Satellite Maintenance 6.11 for RHEL 8 x86_64 (RPMs)"
_repo_client_rhel8 = "Red Hat Satellite Client 6 for RHEL 8 x86_64 (RPMs)"
_release_rhel8 = "8"

_repo_name_capsule_rhel8 = "Red Hat Satellite Capsule 6.11 for RHEL 8 x86_64 RPMs"
_repo_name_maintenance_rhel8 = "Red Hat Satellite Maintenance 6.11 for RHEL 8 x86_64 RPMs"
_repo_name_client_rhel8 = "Red Hat Satellite Client 6 for RHEL 8 x86_64 RPMs"
_productname_capsule = "Red Hat Satellite Capsule"

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

_keyname = "Capsule"
_keyoptions = "--unlimited-hosts --release-version 8 --description 'External Capsule Server'"
_keyoveroptions_base = ("--content-label rhel-8-for-x86_64-baseos-rpms --value 1")
_keyoveroptions_app = ("--content-label rhel-8-for-x86_64-appstream-rpms --value 1")
_keyoveroptions_capsule = ("--content-label satellite-capsule-6.11-for-rhel-8-x86_64-rpms --value 1")
_keyoveroptions_maintenance = ("--content-label satellite-maintenance-6.11-for-rhel-8-x86_64-rpms --value 1")
_keyoveroptions_client = ("--content-label satellite-client-6-for-rhel-8-x86_64-rpms --value 1")

_ports_satellite = "5646/tcp"
_ports_capsule = "53/udp 53/tcp  67/udp 69/udp  80/tcp 443/tcp  5647/tcp  8000/tcp 8140/tcp 8443/tcp 9090/tcp"
_modules = "satellite-capsule:el8"
_packages = "satellite-capsule"

_organizations = "Operations,Finance"
_locations = "Boston,Tokyo"

_role_file = "webserver-role.tgz"
_role_loc = _basedir + "provision-builder/" + _role_file
_dest = "/root/"

_boston_domain = "boston.lab.example.com"
_subnet = "Boston Data Center"
_hostgroup = "Operations Image Builder"

_keyname_9 = "OperationsServers"
_keyoptions_9 = "--unlimited-hosts --release-version 9"
_keyoveroptions_9 = ("--content-label satellite-client-6-for-rhel-8-x86_64-rpms --value 1")

_servera_package1 = "osbuild-composer"
_servera_package2 = "composer-cli"
_servera_package3 = "cockpit-composer"

_dir_repo = "/etc/osbuild-composer/repositories"
_file_toml = "/root/webserver-blueprint.toml"


labname = 'provision-builder'

# Change the class name to match your file name.


class ProvisionBuilder(GuidedExercise):
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
            newcourselib.check_location(_loc_fin, _orgname_fin),
            newcourselib.check_default_org_loc(_orgname_ops, _location),

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base_rhel8, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app_rhel8, _productname),

            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release_rhel9),
            newcourselib.check_repo_added(_repo_capsule_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_maintenance_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_client_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_kickstart_base, _orgname_ops, _release_rhel9_kickstart),
            newcourselib.check_repo_added(_repo_kickstart_app, _orgname_ops, _release_rhel9_kickstart),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_capsule_rhel8, _productname_capsule),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_maintenance_rhel8, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_client_rhel8, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_kickstart_base, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_kickstart_app, _productname),

            newcourselib.check_lifecycle(_orgname_ops, _lcdev, _lcdevdesc, _lclib),
            newcourselib.check_lifecycle(_orgname_ops, _lcqa, _lcqadesc, _lcdev),
            newcourselib.check_lifecycle(_orgname_ops, _lcprod, _lcproddesc, _lcqa),

            newcourselib.check_cv(_orgname_ops, _ops_cv, _ops_cv_desc),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_tools),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_kickstart_base),
            newcourselib.check_repo_cv(_orgname_ops, _ops_cv, _repo_name_kickstart_app),
            newcourselib.check_publish_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _lclib),
            newcourselib.check_promote_cv(_orgname_ops, _ops_cv, _ops_cv_desc, _lcdev),

            newcourselib.check_activation_key(_orgname_ops, _cvdefault, _lclib, _keyname, _keyoptions),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_base),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_app),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_capsule),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_maintenance),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_client),

            newcourselib.check_activation_key(_orgname_ops, _ops_cv, _lcdev, _keyname_9, _keyoptions_9),
            newcourselib.check_key_override(_orgname_ops, _keyname_9, _keyoveroptions_9),

            newcourselib.check_bootstrap_capsule(_orgname_ops, _keyname),
            newcourselib.check_ports(_satellite_host, _ports_satellite),
            newcourselib.check_ports(_capsule_host, _ports_capsule),
            newcourselib.check_yum_module(_capsule_host, _modules),
            newcourselib.check_packages(_capsule_host, _packages),
            newcourselib.check_capsule_certs(_capsule_fqdn),
            newcourselib.check_capsule_install(),
            newcourselib.check_capsule_org_loc(_capsule_fqdn, _organizations, _locations),

            steps.run_command(label="Activate Capsule Services",
                              hosts=["capsule"],
                              command="satellite-installer --scenario capsule"
                              + " --foreman-proxy-dns true"
                              + " --foreman-proxy-dns-interface eth0"
                              + " --foreman-proxy-dns-forwarders 172.25.250.254"
                              + " --foreman-proxy-dns-zone boston.lab.example.com"
                              + " --foreman-proxy-dns-reverse 250.25.172.in-addr.arpa"
                              + " --foreman-proxy-dhcp true"
                              + " --foreman-proxy-dhcp-interface eth0"
                              + " --foreman-proxy-dhcp-range '172.25.250.50 172.25.250.100'"
                              + " --foreman-proxy-dhcp-nameservers 172.25.250.220"
                              + " --foreman-proxy-dhcp-gateway 172.25.250.254"
                              + " --enable-foreman-proxy-plugin-ansible"
                              + " --foreman-proxy-tftp true"
                              + " --foreman-proxy-tftp-managed true"
                              + " --foreman-proxy-tftp-servername 172.25.250.17",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Verify lifecyle on Capsule",
                              hosts=["satellite"],
                              command="hammer capsule content add-lifecycle-environment"
                              + " --name='" + _capsule_fqdn + "'"
                              + " --lifecycle-environment='" + _lcdev + "'"
                              + " --organization='" + _orgname_ops + "';"
                              + " hammer capsule content synchronize"
                              + " --name='" + _capsule_fqdn + "'",
                              returns="0",
                              shell=True
                              ),

            newcourselib.copy_file(_capsule_client, _role_loc, _dest),
            steps.run_command(label="Installing Ansible role on capsule",
                              hosts=_capsule_host,
                              command="tar xzf " + _dest + "/" + _role_file
                              + " -C /etc/ansible/roles/",
                              returns="0",
                              shell=True
                              ),

            newcourselib.create_domain(_location, _boston_domain, _orgname_ops),
            newcourselib.check_capsule_domain(_location, _boston_domain, _orgname_ops, _capsule_fqdn),

            steps.run_command(label="Create Boston subnet",
                              hosts=["satellite"],
                              command="if [[ $(hammer subnet list"
                              + " | grep 'Boston Data Center') ]];"
                              + " then exit 0;"
                              + " else hammer subnet create"
                              + " --name 'Boston Data Center'"
                              + " --boot-mode DHCP"
                              + " --organizations='" + _orgname_ops + "'"
                              + " --locations='" + _location + "'"
                              + " --dns='" + _capsule_fqdn + "'"
                              + " --dhcp='" + _capsule_fqdn + "'"
                              + " --tftp='" + _capsule_fqdn + "'"
                              + " --ipam DHCP"
                              + " --network 172.25.250.0 --mask 255.255.255.0"
                              + " --dns-primary 172.25.250.220"
                              + " --domains='" + _boston_domain + "'; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Verify Operations Provisioning hostgroup",
                              hosts=["satellite"],
                              command="if [[ $(hammer hostgroup list"
                              + " | grep 'Operations Provisioning') ]];"
                              + " then exit 0;"
                              + " else hammer hostgroup create"
                              + " --name 'Operations Provisioning'"
                              + " --lifecycle-environment='" + _lcdev + "'"
                              + " --content-view='" + _ops_cv + "'"
                              + " --content-source='" + _capsule_fqdn + "'"
                              + " --domain='" + _boston_domain + "'"
                              + " --subnet='" + _subnet + "'"
                              + " --architecture='x86_64'"
                              + " --operatingsystem='RedHat 9.0'"
                              + " --partition-table='Kickstart default'"
                              + " --pxe-loader='PXELinux BIOS'"
                              + " --location='" + _location + "'"
                              + " --organization='" + _orgname_ops + "'; fi",
                              returns="0",
                              shell=True
                              ),

            newcourselib.register_host(_servera_host, _orgname_ops, _environmentBase),

            steps.run_command(label="Verify osbuild-composer package on servera",
                              hosts=["servera"],
                              command="if [[ $(yum list installed"
                              + " | grep '" + _servera_package1 + "') ]];"
                              + " then yum -y remove"
                              + " '" + _servera_package1 + "'; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Verify composer-cli package on servera",
                              hosts=["servera"],
                              command="if [[ $(yum list installed"
                              + " | grep '" + _servera_package2 + "') ]];"
                              + " then yum -y remove"
                              + " '" + _servera_package2 + "'; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Verify cockpit-composer package on servera",
                              hosts=["servera"],
                              command="if [[ $(yum list installed"
                              + " | grep '" + _servera_package3 + "') ]];"
                              + " then yum -y remove"
                              + " '" + _servera_package3 + "'; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Verify osbuild-composer.socket on servera",
                              hosts=["servera"],
                              command="if [[ $(systemctl is-active osbuild-composer.socket | grep ^active) ]];"
                              + " then systemctl disable --now osbuild-composer.socket; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Verify webserver-blueprint.toml file on servera",
                              hosts=["servera"],
                              command="if [[ -f '" + _file_toml + "' ]];"
                              + " then rm -rf"
                              + " '" + _file_toml + "'; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Remove custom image on capsule",
                              hosts=_capsule_host,
                              command="rm -Rf /var/www/html/pub/*.tar.xz ",
                              returns="0",
                              shell=True
                              ),

            newcourselib.check_directory(_servera_host, _dir_repo),
            newcourselib.copy_file(_servera_client, _file_loc, _dir_repo),
            steps.run_command(label="Check the entitlement keys in rhel-90.json file",
                              hosts=["servera"],
                              command="""
                                sed -i "s/changeme/$(ls /etc/pki/entitlement/ | grep -oE '[0-9]+' | head -n1)/" /etc/osbuild-composer/repositories/rhel-90.json
                                """,
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Check Ansible role provision",
                              hosts=["satellite"],
                              command="""
                                hammer settings set --name remote_execution_connect_by_ip --value yes
                                """,
                              returns="0",
                              shell=True
                              ),

            newcourselib.remove_host(_orgname_ops, _servere_fqdn),
            newcourselib.remove_hostgroup(_hostgroup),
        ]
        Console(items).run_items(action="Starting")

    def finish(self):
        """
        Perform any post-lab cleanup tasks.
        """
        items = [
            newcourselib.verify_systems(_targets),

            steps.run_command(label="Check Ansible role provision",
                              hosts=["satellite"],
                              command="""
                                hammer settings set --name remote_execution_connect_by_ip --value no
                                """,
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Stop leasing from dhcp",
                              hosts=["capsule"],
                              command="if [[ $(systemctl is-active dhcpd | grep ^active) ]]; then"
                              + " systemctl stop dhcpd;"
                              + " rm -rf /var/lib/dhcpd/dhcpd.leases;"
                              + " touch /var/lib/dhcpd/dhcpd.leases;"
                              + " systemctl start dhcpd;"
                              + " fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Clean DNS",
                              hosts=["capsule"],
                              command="if [[ $(systemctl is-active named.service | grep ^active) ]]; then"
                              + " systemctl stop named.service;"
                              + " sed -i '/servere/d' /var/named/dynamic/db.250.25.172.in-addr.arpa;"
                              + " sed -i '/servere/d' /var/named/dynamic/db.boston.lab.example.com;"
                              + " rm -f /var/named/dynamic/*jnl;"
                              + " systemctl start named.service;"
                              + " fi",
                              returns="0",
                              shell=True
                              ),
        ]
        Console(items).run_items(action="Finishing")
