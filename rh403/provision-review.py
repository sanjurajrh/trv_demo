#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Aug 9 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - original code
# * Mar 10 2023 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 provision.
This module implements the start and finish functions for the
Provision Review Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "capsule"]
_satellite_host = ["satellite"]
_capsule_host = ["capsule"]
_capsule_fqdn = "capsule.lab.example.com"
_servere_host = ["servere"]
_servere_fqdn = "servere.tokyo.lab.example.com"
_orgname_ops = "Operations"
_location_ops = "Boston"
_orgname_fin = "Finance"
_location_fin = "Tokyo"

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
_lcbuild = "Build"
_lcbuilddesc = "Build"
_lctest = "Test"
_lctestdesc = "Test"
_lcdeploy = "Deploy"
_lcdeploydesc = "Deploy"

_cvdefault = "Default Organization View"

_ops_cv = "OperationsServerBase"
_ops_cv_desc = "Base Packages"
_fin_cv = "FinanceServerBase"
_fin_cv_desc = "Base Packages"

_keyname = "Capsule"
_keyoptions = "--unlimited-hosts --release-version 8 --description 'External Capsule Server'"
_keyoveroptions_base = ("--content-label rhel-8-for-x86_64-baseos-rpms --value 1")
_keyoveroptions_app = ("--content-label rhel-8-for-x86_64-appstream-rpms --value 1")
_keyoveroptions_capsule = ("--content-label satellite-capsule-6.11-for-rhel-8-x86_64-rpms --value 1")
_keyoveroptions_maintenance = ("--content-label satellite-maintenance-6.11-for-rhel-8-x86_64-rpms --value 1")
_keyoveroptions_client = ("--content-label satellite-client-6-for-rhel-8-x86_64-rpms --value 1")

_organizations = "Operations,Finance"
_locations = "Boston,Tokyo"

_ports_satellite = "5646/tcp"
_ports_capsule = "53/udp 53/tcp  67/udp 69/udp  80/tcp 443/tcp  5647/tcp  8000/tcp 8140/tcp 8443/tcp 9090/tcp"
_modules = "satellite-capsule:el8"
_packages = "satellite-capsule"

_tokyo_domain = "tokyo.lab.example.com"
_subnet = "Tokyo Data Center"
_hostgroup = "Finance Provisioning Group"

_keyname_9 = "FinanceServers"
_keyoptions_9 = "--unlimited-hosts --release-version 9"
_keyoveroptions_9 = ("--content-label satellite-client-6-for-rhel-8-x86_64-rpms --value 1")

labname = 'provision-review'

# Change the class name to match your file name.


class ProvisionReview(GuidedExercise):
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
            newcourselib.verify_organization_cdn(_orgname_fin),
            newcourselib.check_location(_location_ops, _orgname_ops),
            newcourselib.check_location(_location_fin, _orgname_fin),
            newcourselib.check_default_org_loc(_orgname_fin, _location_fin),

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.check_sync_product_repos(_orgname_fin, _productname),

            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base_rhel8, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app_rhel8, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_app, _productname),

            newcourselib.check_repo_added(_repo_capsule_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_maintenance_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_client_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_tools, _orgname_fin, _release_rhel9),
            newcourselib.check_repo_added(_repo_kickstart_base, _orgname_fin, _release_rhel9_kickstart),
            newcourselib.check_repo_added(_repo_kickstart_app, _orgname_fin, _release_rhel9_kickstart),

            newcourselib.check_sync_repo(_orgname_ops, _repo_name_capsule_rhel8, _productname_capsule),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_maintenance_rhel8, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_client_rhel8, _productname),
            newcourselib.check_sync_repo(_orgname_fin, _repo_name_tools, _productname),
            newcourselib.check_sync_repo(_orgname_fin, _repo_name_kickstart_base, _productname),
            newcourselib.check_sync_repo(_orgname_fin, _repo_name_kickstart_app, _productname),

            newcourselib.check_activation_key(_orgname_ops, _cvdefault, _lclib, _keyname, _keyoptions),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_base),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_app),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_capsule),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_maintenance),
            newcourselib.check_key_override(_orgname_ops, _keyname, _keyoveroptions_client),

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
                              + " --foreman-proxy-dns-zone tokyo.lab.example.com"
                              + " --foreman-proxy-dns-reverse 250.25.172.in-addr.arpa"
                              + " --foreman-proxy-dhcp true"
                              + " --foreman-proxy-dhcp-interface eth0"
                              + " --foreman-proxy-dhcp-range '172.25.250.50 172.25.250.100'"
                              + " --foreman-proxy-dhcp-nameservers 172.25.250.220"
                              + " --foreman-proxy-dhcp-gateway 172.25.250.254"
                              + " --foreman-proxy-tftp true"
                              + " --foreman-proxy-tftp-managed true"
                              + " --foreman-proxy-tftp-servername 172.25.250.17",
                              returns="0",
                              shell=True
                              ),

            newcourselib.check_lifecycle(_orgname_fin, _lcbuild, _lcbuilddesc, _lclib),
            newcourselib.check_lifecycle(_orgname_fin, _lctest, _lctestdesc, _lcbuild),
            newcourselib.check_lifecycle(_orgname_fin, _lcdeploy, _lcdeploydesc, _lctest),


            newcourselib.check_cv(_orgname_fin, _fin_cv, _fin_cv_desc),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_tools),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_kickstart_base),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_kickstart_app),
            newcourselib.check_publish_cv(_orgname_fin, _fin_cv, _fin_cv_desc, _lclib),
            newcourselib.check_promote_cv(_orgname_fin, _fin_cv, _fin_cv_desc, _lcbuild),

            newcourselib.check_activation_key(_orgname_fin, _fin_cv, _lcbuild, _keyname_9, _keyoptions_9),
            newcourselib.check_key_override(_orgname_fin, _keyname_9, _keyoveroptions_9),

            newcourselib.create_domain(_location_fin, _tokyo_domain, _orgname_fin),
            newcourselib.check_capsule_domain(_location_fin, _tokyo_domain, _orgname_fin, _capsule_fqdn),
            steps.run_command(label="Create Tokyo subnet",
                              hosts=["satellite"],
                              command="if [[ $(hammer subnet list"
                              + " | grep 'Tokyo Data Center') ]];"
                              + " then exit 0;"
                              + " else hammer subnet create"
                              + " --name 'Tokyo Data Center'"
                              + " --boot-mode DHCP"
                              + " --organizations='" + _orgname_fin + "'"
                              + " --locations='" + _location_fin + "'"
                              + " --dns='" + _capsule_fqdn + "'"
                              + " --dhcp='" + _capsule_fqdn + "'"
                              + " --tftp='" + _capsule_fqdn + "'"
                              + " --ipam DHCP"
                              + " --network 172.25.250.0 --mask 255.255.255.0"
                              + " --dns-primary 172.25.250.220"
                              + " --domains='" + _tokyo_domain + "'; fi",
                              returns="0",
                              shell=True
                              ),

            steps.run_command(label="Stop leasing from dhcp",
                              hosts=["capsule"],
                              command="systemctl stop dhcpd"
                              + " ; rm -rf /var/lib/dhcpd/dhcpd.leases"
                              + " ; touch /var/lib/dhcpd/dhcpd.leases"
                              + " ; systemctl start dhcpd",
                              returns="0",
                              shell=True
                              ),

            newcourselib.remove_host(_orgname_fin, _servere_fqdn),
            newcourselib.remove_hostgroup(_hostgroup),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),

            steps.run_command(label="Verify Kickstart BaseOS repo in FinanceServerBase content view",
                              hosts=_satellite_host,
                              command="hammer"
                              + " content-view info"
                              + " --organization " + _orgname_fin
                              + " --name='FinanceServerBase'"
                              + " | grep 'Red_Hat_Enterprise_Linux_9_for_x86_64_-_BaseOS_Kickstart_9_0'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Kickstart AppStream repo in FinanceServerBase content view",
                              hosts=_satellite_host,
                              command="hammer"
                              + " content-view info"
                              + " --organization " + _orgname_fin
                              + " --name='FinanceServerBase'"
                              + " | grep 'Red_Hat_Enterprise_Linux_9_for_x86_64_-_AppStream_Kickstart_9_0'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify DNS, DHCP, and TFTP services on the Capsule",
                              hosts=_satellite_host,
                              command="if [[ $(hammer"
                              + " capsule info"
                              + " --name='" + _capsule_fqdn + "'"
                              + " | grep -E 'DHCP|DNS|TFTP' | wc -l) == 3 ]];"
                              + " then exit 0;"
                              + " else exit 1; fi",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Tokyo domain exists",
                              hosts=_satellite_host,
                              command="hammer"
                              + " domain list"
                              + " --organization " + _orgname_fin
                              + " | grep 'tokyo.lab.example.com'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Organization and Location for Tokyo domain",
                              hosts=_satellite_host,
                              command="if [[ $(hammer"
                              + " domain info"
                              + " --organization " + _orgname_fin
                              + " --name='tokyo.lab.example.com'"
                              + " --fields 'Locations,Organizations'"
                              + " | grep -E 'Finance|Tokyo' | wc -l) == 2 ]];"
                              + " then exit 0;"
                              + " else exit 1; fi",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Tokyo Data Center subnet exists",
                              hosts=_satellite_host,
                              command="hammer"
                              + " subnet list"
                              + " --organization " + _orgname_fin
                              + " | grep 'Tokyo Data Center'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Finance Provisioning exists",
                              hosts=_satellite_host,
                              command="hammer"
                              + " hostgroup list"
                              + " | grep 'Finance Provisioning'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify servere.tokyo.lab.example.com exists",
                              hosts=_satellite_host,
                              command="hammer"
                              + " host list"
                              + " --organization " + _orgname_fin
                              + " | grep 'servere.tokyo.lab.example.com'",
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
