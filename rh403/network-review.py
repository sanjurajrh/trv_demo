#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Jul 13 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - original code
# * Jul 28 2022 Bernardo Gargallo <bgargallo@redhat.com>
#   - update to Sat 6.11
# * Nov 10 2022 Mauricio Santacruz <msantacruz@redhat.com>
#   - Added validation in "Update Capsule organization and location" step
#   - Using "update_capsule_org_loc" function
# * Feb 03 2023 Alex Callejas <acalleja@redhat.com>
#   - Migrate to new course library
#   - Check steps
# * Mar 8 2023 Alex Callejas <acalleja@redhat.com>
#   - Capsule installation adjustments

"""
Lab script for RH403 network.
This module implements the start and finish functions for the
Network Review Red Hat Content guided exercise.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "capsule"]
_satellite_host = ["satellite"]
_capsule_host = ["capsule"]
_capsule_fqdn = "capsule.lab.example.com"
_orgname_ops = "Operations"
_orgname_fin = "Finance"
_location_ops = "Boston"
_location = "Tokyo"

_basedir = "/home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/network-review/"
_script = "check_cv_netconf.sh"

_repo_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 (RPMs)"

_repo_name_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS RPMs 9"
_repo_name_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream RPMs 9"
_repo_name_tools = "Red Hat Satellite Client 6 for RHEL 9 x86_64 RPMs"
_productname = "Red Hat Enterprise Linux for x86_64"
_release_rhel9 = "9"

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
_lcbuild = "Build"
_lcbuilddesc = "Build"
_lctest = "Test"
_lctestdesc = "test"
_lcdeploy = "Deploy"
_lcdeploydesc = "Deploy"

_cvdefault = "Default Organization View"

_fin_cv = "FinanceServerBase"
_fin_cv_desc = "Base Packages"

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

_repo_kickstart_base = "Red Hat Enterprise Linux 9 for x86_64 - BaseOS Kickstart 9.0"
_repo_kickstart_app = "Red Hat Enterprise Linux 9 for x86_64 - AppStream Kickstart 9.0"
_product_kickstart = "Red Hat Enterprise Linux for x86_64"

_subnet = "Tokyo Data Center"
_domain = "tokyo.lab.example.com"

labname = 'network-review'

# Change the class name to match your file name.


class NetworkReview(GuidedExercise):
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
            newcourselib.check_location(_location, _orgname_fin),
            newcourselib.check_location(_location_ops, _orgname_ops),
            newcourselib.check_default_org_loc(_orgname_fin, _location),

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.check_sync_product_repos(_orgname_fin, _productname),

            newcourselib.check_file_in_satellite(_basedir, _script),
            newcourselib.check_script(_satellite_host, _script),

            newcourselib.verify_repository(_orgname_ops, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base_rhel8, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app_rhel8, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_base, _productname),
            newcourselib.verify_repository(_orgname_fin, _repo_name_app, _productname),

            newcourselib.check_repo_added(_repo_tools, _orgname_fin, _release_rhel9),
            newcourselib.check_repo_added(_repo_tools, _orgname_ops, _release_rhel9),
            newcourselib.check_repo_added(_repo_capsule_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_maintenance_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_repo_added(_repo_client_rhel8, _orgname_ops, _release_rhel8),
            newcourselib.check_sync_repo(_orgname_fin, _repo_name_tools, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_tools, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_capsule_rhel8, _productname_capsule),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_maintenance_rhel8, _productname),
            newcourselib.check_sync_repo(_orgname_ops, _repo_name_client_rhel8, _productname),

            newcourselib.check_lifecycle(_orgname_fin, _lcbuild, _lcbuilddesc, _lclib),
            newcourselib.check_lifecycle(_orgname_fin, _lctest, _lctestdesc, _lcbuild),
            newcourselib.check_lifecycle(_orgname_fin, _lcdeploy, _lcdeploydesc, _lctest),

            newcourselib.check_cv(_orgname_fin, _fin_cv, _fin_cv_desc),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_base),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_app),
            newcourselib.check_repo_cv(_orgname_fin, _fin_cv, _repo_name_tools),
            newcourselib.check_publish_cv(_orgname_fin, _fin_cv, _fin_cv_desc, _lclib),
            newcourselib.check_promote_cv(_orgname_fin, _fin_cv, _fin_cv_desc, _lcbuild),

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

            newcourselib.remove_subnet(_domain, _subnet),
            steps.run_command(label="Remove services in Capsule Server",
                              hosts=["capsule"],
                              command="satellite-installer --scenario capsule"
                              + " --foreman-proxy-dns false"
                              + " --foreman-proxy-dhcp false"
                              + " --foreman-proxy-tftp false"
                              + " --no-enable-foreman-proxy-plugin-discovery",
                              returns="0",
                              shell=True
                              ),
            newcourselib.remove_domain(_domain),
            newcourselib.remove_capsule_lc(_capsule_fqdn, _orgname_fin, _lcbuild),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),

            steps.run_command(label="Verify Kickstart BaseOS repo is enabled",
                              hosts=_satellite_host,
                              command="hammer"
                              + " repository list"
                              + " --organization " + _orgname_fin
                              + " | grep '" + _repo_kickstart_base + "'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Kickstart BaseOS repo is synced",
                              hosts=_satellite_host,
                              command="hammer"
                              + " repository info"
                              + " --organization " + _orgname_fin
                              + " --name='" + _repo_kickstart_base + "'"
                              + " --product='" + _product_kickstart + "'"
                              + " | grep 'Status:.*Success'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Kickstart AppStream repo is enabled",
                              hosts=_satellite_host,
                              command="hammer"
                              + " repository list"
                              + " --organization " + _orgname_fin
                              + " | grep '" + _repo_kickstart_app + "'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Kickstart AppStream repo is synced",
                              hosts=_satellite_host,
                              command="hammer"
                              + " repository info"
                              + " --organization " + _orgname_fin
                              + " --name='" + _repo_kickstart_app + "'"
                              + " --product='" + _product_kickstart + "'"
                              + " | grep 'Status:.*Success'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Kickstart BaseOS repo in Base content view",
                              hosts=_satellite_host,
                              command="hammer"
                              + " content-view info"
                              + " --organization " + _orgname_fin
                              + " --name='" + _fin_cv + "'"
                              + " | grep '" + _repo_kickstart_base + "'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Kickstart AppStream repo in Base content view",
                              hosts=_satellite_host,
                              command="hammer"
                              + " content-view info"
                              + " --organization " + _orgname_fin
                              + " --name='" + _fin_cv + "'"
                              + " | grep '" + _repo_kickstart_app + "'",
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

            steps.run_command(label="Verify network address for the subnet",
                              hosts=_satellite_host,
                              command="hammer"
                              + " subnet info"
                              + " --organization " + _orgname_fin
                              + " --name 'Tokyo Data Center'"
                              + " | grep 'Network Addr:.*172.25.250.0'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify IP range for the subnet",
                              hosts=_satellite_host,
                              command="if [[ $(hammer"
                              + " subnet info"
                              + " --organization " + _orgname_fin
                              + " --name='Tokyo Data Center'"
                              + " | grep -e 'Start of IP Range:.*172.25.250.50'"
                              + " -e 'End of IP Range:.*172.25.250.100' | wc -l) == 2 ]];"
                              + " then exit 0;"
                              + " else exit 1; fi",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify domain for the subnet",
                              hosts=_satellite_host,
                              command="hammer"
                              + " subnet info"
                              + " --organization " + _orgname_fin
                              + " --name='Tokyo Data Center'"
                              + " --fields 'Domains'"
                              + " | grep 'tokyo.lab.example.com'",
                              returns=0,
                              shell=True,
                              ),

            steps.run_command(label="Verify Capsule for the subnet",
                              hosts=_satellite_host,
                              command="if [[ $(hammer"
                              + " subnet info"
                              + " --organization " + _orgname_fin
                              + " --name='Tokyo Data Center'"
                              + " --fields='Smart Proxies'"
                              + " | grep -e 'DNS:.*capsule.lab.example.com'"
                              + " -e 'TFTP:.*capsule.lab.example.com'"
                              + " -e 'DHCP:.*capsule.lab.example.com' | wc -l) == 3 ]];"
                              + " then exit 0;"
                              + " else exit 1; fi",
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
