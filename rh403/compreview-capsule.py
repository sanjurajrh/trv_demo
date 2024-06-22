#
# Copyright (c) 2022 Red Hat Training <training@redhat.com>
#
# All rights reserved.
# No warranty, explicit or implied, provided.
#
# CHANGELOG
# * Aug 18 2022 Alex Callejas <acalleja@redhat.com>
#   - original code
# * Mar 01 2023 Mauricio Santacruz <msantacruz@redhat.com>
#   - Migrate to new course library
#   - Check steps

"""
Lab script for RH403 software.
This module implements the start and finish functions for the
install and configure a Satellite Capsule Server laboratory.
"""

from . import newcourselib
from labs.common import steps
from labs.common.userinterface import Console
from labs.grading import Default as GuidedExercise

_targets = ["satellite", "capsule", "serverc", "servere"]
_satellite_host = ["satellite"]
_capsule_hosts = ["satellite", "capsule"]
_capsule_host = ["capsule"]
_capsule_fqdn = "capsule.lab.example.com"
_servere_host = ["servere"]
_servere_fqdn = "servere.lab.example.com"

_orgname_ops = "Operations"
_orgname_fin = "Finance"

_location_fin = "San Francisco"

_repo_name_base_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - BaseOS RPMs 8"
_repo_name_app_rhel8 = "Red Hat Enterprise Linux 8 for x86_64 - AppStream RPMs 8"
_productname = "Red Hat Enterprise Linux for x86_64"

_repo_client_rhel8 = "Red Hat Satellite Client 6 for RHEL 8 x86_64 (RPMs)"
_repo_maintenance_rhel8 = "Red Hat Satellite Maintenance 6.11 for RHEL 8 x86_64 (RPMs)"
_repo_capsule_rhel8 = "Red Hat Satellite Capsule 6.11 for RHEL 8 x86_64 (RPMs)"
_release_rhel8 = "8"

_keyname = "Capsule"

_packages = "foreman-proxy-content satellite-capsule"
_cert_files = "/root/capsule_cert*"

_ports_capsule = "53/udp 53/tcp  67/udp 69/udp  80/tcp 443/tcp  5647/tcp  8000/tcp 8140/tcp  8443/tcp 9090/tcp"
_ports_satellite = "5646/tcp"


labname = 'compreview-capsule'

# Change the class name to match your file name.


class ComprehensiveCapsule(GuidedExercise):
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

            newcourselib.check_location(_location_fin, _orgname_fin),

            newcourselib.check_sync_product_repos(_orgname_ops, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_base_rhel8, _productname),
            newcourselib.verify_repository(_orgname_ops, _repo_name_app_rhel8, _productname),

            newcourselib.remove_activation_key(_orgname_ops, _keyname),
            newcourselib.remove_capsule(_capsule_fqdn),
            newcourselib.remove_packages(_capsule_host, _packages),
            newcourselib.remove_file_directory(_capsule_hosts, _cert_files),
            newcourselib.remove_ports(_capsule_host, _ports_capsule),
            newcourselib.remove_ports(_satellite_host, _ports_satellite),
            newcourselib.unregister_host(_capsule_host),
            newcourselib.remove_host(_orgname_ops, _capsule_fqdn),
            newcourselib.unregister_host(_servere_host),
            newcourselib.remove_host(_orgname_fin, _servere_fqdn),
            newcourselib.disable_repo(_orgname_ops, _repo_client_rhel8, _release_rhel8),
            newcourselib.disable_repo(_orgname_ops, _repo_capsule_rhel8, _release_rhel8),
            newcourselib.disable_repo(_orgname_ops, _repo_maintenance_rhel8, _release_rhel8),
        ]
        Console(items).run_items(action="Starting")

    def grade(self):
        """Perform evaluation steps on the system."""
        items = [
            newcourselib.verify_systems(_targets),
            steps.run_command(label="Verify activation key",
                              hosts=_satellite_host,
                              command="hammer --no-headers"
                              + " activation-key list"
                              + " --organization " + _orgname_ops
                              + " --fields Name"
                              + " | grep '" + _keyname + "'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify host registration",
                              hosts=_satellite_host,
                              command="hammer --no-headers"
                              + " host list "
                              + " --organization " + _orgname_ops
                              + " --fields Name"
                              + " | grep '" + _capsule_fqdn + "'",
                              returns=0,
                              shell=True,
                              ),
            steps.run_command(label="Verify capsule server",
                              hosts=_satellite_host,
                              command="hammer --no-headers"
                              + " capsule list "
                              + " --organization " + _orgname_fin
                              + " --fields Name"
                              + " | grep '" + _capsule_fqdn + "'",
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
