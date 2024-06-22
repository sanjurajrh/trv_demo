"""
RH403 course library

To use these functions, add an import statement to your lab scripts:
from . import newcourselib

"""

from labs.common import tasks
from labs.common import labtools


def verify_systems(host):
    """
    """
    return {
        "label": "Verify lab systems",
        "task": labtools.check_host_reachable,
        "hosts": host,
        "fatal": True
    }


def satellite_status():
    """
    Verifies the satellite server status.
    Fails if the satellite status is not OK.
    """
    return {
        "label": "Verify Satellite status",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "satellite-maintain service status",
        "returns": 0,
        "prints": "OK",
        "options": [],
        "fatal": True,
        "student_msg": "Run 'satellite-maintain service restart' in satellite machine.",
        "sshkey": '',
        "shell": True
    }


def check_default_org_loc(orgname, locname):
    """
    Set the default login to the given organization and location names
    'orgname' is a str with the organization to be the default
    'locname' is a str with the location to be the default
    """
    return {
        "label": f"Check login default to '{orgname}' and '{locname}'",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer user update --login admin"
                    + " --default-organization='" + orgname + "'"
                    + " --default-location='" + locname + "') ]];"
                    + " then exit 0; else: exit 1; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot set the default organization and location.",
        "sshkey": '',
        "shell": True
    }


def verify_cdn_listing():
    """
    Verify CDN listing.
    Fails if the CDN status is not OK.
    """
    return {
        "label": "Verify CDN listing",
        "task": tasks.run_command,
        "hosts": ["workstation"],
        "command": "curl http://cdn.lab.example.com/listing",
        "returns": "0",
        "prints": 'content',
        "options": [],
        "fatal": True,
        "student_msg": "CDN status is not OK",
        "sshkey": '',
        "shell": True
    }


def verify_organization_cdn(orgname):
    """
    Verify organization CDN.
    'orgname' is a str with the organization name to be verified.
    Fails if the CDN is not local or configured.
    """
    return {
        "label": f"Verify '{orgname}' CDN",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer organization info"
                    + " --name " + orgname
                    + " --fields='Cdn configuration/url'"
                    + " | grep 'http://cdn.lab.example.com') ]];"
                    + " then exit 0;"
                    + " else hammer organization update"
                    + " --name " + orgname
                    + " --redhat-repository-url 'http://cdn.lab.example.com';"
                    + " exit 0; fi",
        "returns": "0",
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "CDN status is not OK",
        "sshkey": '',
        "shell": True
    }


def verify_organization(orgname):
    """
    Verify the organization given as parameter.
    'orgname' is a str with the organization name to be verified.
    """
    return {
        "label": f"Verify '{orgname}' organization exists",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer organization info --name='" + orgname + "' "
                    + " | grep 'Label:.*" + orgname + "'",
        "returns": "0",
        "prints": '',
        "options": [],
        "fatal": True,
        "student_msg": "The organization is not created",
        "sshkey": '',
        "shell": True
    }


def check_organization(orgname, orgdesc):
    """
    Creates the organization given as parameter.
    'orgname' is a str with the organization name to be created
    'orgdesc' is a str with the organization description
    """
    return {
        "label": f"Check the '{orgname}' organization exists",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer organization info --name='" + orgname + "' "
                    + " | grep 'Label:.*" + orgname + "' ) ]];"
                    + "then exit 0;"
                    + "else hammer organization create --name='" + orgname + "'"
                    + " --description='" + orgdesc + "';"
                    + "exit $?; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot create organization. "
                       + "The organization might exist with incorrect parameters.",
        "sshkey": '',
        "shell": True
    }


def verify_default_location():
    """
    Verify the default location.
    """
    return {
        "label": "Verify the 'Default Location' exists",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer location info --name='Default Location'",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": True,
        "student_msg": "Default Location cannot be found.",
        "sshkey": '',
        "shell": True
    }


def verify_default_organization():
    """
    Verify the default organization.
    """
    return {
        "label": "Verify the 'Default Organization' exists",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer organization info --name='Default Organization'",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": True,
        "student_msg": "Default Organization cannot be found.",
        "sshkey": '',
        "shell": True
    }


def check_manifest_in_satellite(basedir, manifest):
    """
    Check the manifest file.
    'manifest' is a str with the manifest filename to be checked.
    """
    return {
        "label": f"Check '{manifest}' file exists in satellite",
        "task": tasks.run_command,
        "hosts": ["workstation"],
        "command": "scp " + basedir + manifest + " root@satellite:" + manifest,
        "returns": "0",
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "The manifest is not present",
        "sshkey": '',
        "shell": True
    }


def check_file_in_satellite(basedir, file):
    """
    Check a file in satellite.
    'basedir' is a str with the path
    'file' is a str with the filename to be checked.
    """
    return {
        "label": f"Check '{file}' file exists in satellite",
        "task": tasks.run_command,
        "hosts": ["workstation"],
        "command": "scp " + basedir + file + " root@satellite:" + file,
        "returns": "0",
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "The file is not present",
        "sshkey": '',
        "shell": True
    }


def check_manifest_in_workstation(basedir, manifest):
    """
    Check the manifest file.
    'manifest' is a str with the manifest filename to be checked.
    """
    return {
        "label": f"Verify '{manifest}' file exists in workstation",
        "task": tasks.run_command,
        "hosts": ["workstation"],
        "command": "cp " + basedir + manifest + " /home/student/" + manifest,
        "returns": "0",
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "The manifest is not present",
        "sshkey": '',
        "shell": True
    }


def check_manifest(orgname, manifest):
    """
    Verifies if the manifest exists in the organization, and if not it
    downloads if from the repo url and installs it.
    'orgname' is a str with the organization to place the manifest
    'manifest' is a str with the manifest path name
    """
    return {
        "label": f"Check manifest in '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer subscription list --organization='" + orgname + "'"
                    + " | grep 'Red Hat Enterprise Linux Server, Standard (Physical or Virtual Nodes)') ]];"
                    + " then exit 0;"
                    + " else if [[ -f /root/" + manifest + " ]];"
                    + " then hammer organization update --name='" + orgname + "' --redhat-repository-url=http://cdn.lab.example.com "
                    + " && hammer subscription upload --file='/root/" + manifest + "' --organization='"
                    + orgname + "'; exit 0; fi; exit 1; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot import the manifest.",
        "sshkey": '',
        "shell": True
    }


def delete_manifest(orgname):
    """
    Remove the manifest in the organization.
    'orgname' is a str with the organization to place the manifest
    'manifest' is a str with the manifest path name
    """
    return {
        "label": f"Remove manifest in '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer subscription list --organization='" + orgname + "'"
                    + " | grep 'Red Hat Enterprise Linux Server, Standard (Physical or Virtual Nodes)') ]];"
                    + " then hammer subscription delete-manifest"
                    + " --organization '" + orgname + "'; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the manifest.",
        "sshkey": '',
        "shell": True
    }


def verify_repository(orgname, reponame, productname):
    """
    Synchronizes the repositories for the given product in the given organization.
    'orgname' is a str with the organization to verify the repo.
    'reponame' is a str with the repository name to be verified.
    'productname' is a str with the product name.
    """
    return {
        "label": f"Verify '{reponame}' for '{orgname}' organization exists",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer repository info --name='" + reponame + "'"
                    + " --organization='" + orgname + "'"
                    + " --product='" + productname + "'"
                    + " --fields Sync/status",
        "returns": 0,
        "prints": 'Success',
        "options": [],
        "fatal": True,
        "student_msg": "Repository is not synced.",
        "sshkey": '',
        "shell": True
    }


def remove_org(orgname):
    """
    Removes the organization given as parameter.
    'orgname' is a str with the organization name to be removed
    """
    return {
        "label": f"Remove '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer organization info --name='" + orgname + "') ]];"
                    + "then hammer organization delete --name='" + orgname + "';"
                    + "exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove organization.",
        "sshkey": '',
        "shell": True
    }


def check_collection(orgname, collection):
    """
    Create the collection in the given organization
    'orgname' is a str with the organization
    'collection' is a str with the collection name
    """
    return {
        "label": f"Check '{collection}' host collection",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer host-collection list --organization='" + orgname + "'"
                    + " | grep '" + collection + "') ]];"
                    + " then exit 0;"
                    + " else hammer host-collection create"
                    + " --organization='" + orgname + "' --name='" + collection + "';"
                    + " exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot create collection.",
        "sshkey": '',
        "shell": True
    }


def remove_collection(orgname, collection):
    """
    Remove the collection from the given organization
    'orgname' is a str with the organization
    'collection' is a str with the collection name
    """
    return {
        "label": f"Remove '{collection}' host collection",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer host-collection list --organization='" + orgname + "'"
                    + " | grep '" + collection + "') ]];"
                    + " then hammer host-collection delete"
                    + " --organization='" + orgname + "' --name='" + collection + "';"
                    + " exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove collection.",
        "sshkey": '',
        "shell": True
    }


def check_location(locname, orgname):
    """
    Creates the location given as parameter inside the organization.
    'locname' is a str with the location name to be created
    'orgname' is a str with the organization where the location will be created
    """
    return {
        "label": f"Check '{locname}' location exists inside '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer location info --name='" + locname + "') ]];"
                    + " then hammer location add-organization --name='" + locname + "'"
                    + " --organization='" + orgname + "'; exit 0;"
                    + " else hammer location create --name='" + locname + "'"
                    + " && hammer location add-organization --name='" + locname + "'"
                    + " --organization='" + orgname + "';"
                    + " exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot create location.",
        "sshkey": '',
        "shell": True
    }


def remove_location(locname):
    """
    Removes the location given as parameter inside the organization.
    'locname' is a str with the location name to be removed
    """
    return {
        "label": f"Remove '{locname}' location",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer location info --name='" + locname + "') ]];"
                    + "then hammer location delete --name='" + locname + "';"
                    + "exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove location.",
        "sshkey": '',
        "shell": True
    }


def disable_repo(orgname, reponame, release):
    """
    Verifies if the given repo is enabled and disable it in the given
    organization.
    'orgname' is a str with the organization to disable the repo.
    'reponame' is a str with the repository name.
    'release' is a str with the release version.
    """
    return {
        "label": f"Check '{reponame}' repository is not in '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer repository-set list"
                    + " --organization='" + orgname + "'"
                    + " --enabled=yes | grep '" + reponame + "') ]]; then"
                    + " hammer repository-set disable"
                    + " --organization='" + orgname + "'"
                    + " --name='" + reponame + "'"
                    + " --basearch='x86_64'"
                    + " --releasever='" + release + "';"
                    + " fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot disable the repository.",
        "sshkey": '',
        "shell": True
    }


def remove_repository(orgname, repository, product):
    """
    Removes the given repository in the given organization.
    'orgname' is a str with the organization.
    'repository' is a str with the repository name.
    'repository' is a str with the repository name.
    'product' is a str with the product name.
    """
    return {
        "label": f"Check '{repository}' repo is not in '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer repository info --name='" + repository + "' "
                    + "--organization='" + orgname + "' "
                    + "--product='" + product + "') ]]; "
                    + "then hammer repository delete "
                    + "--organization='" + orgname + "' "
                    + "--product='" + product + "' "
                    + "--name='" + repository + "'; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove repository.",
        "sshkey": '',
        "shell": True
    }


def remove_sync_plan(orgname, syncplan):
    """
    Removes the given repository in the given organization.
    'orgname' is a str with the organization.
    'syncplan' is a str with the sync plan name.
    """
    return {
        "label": f"Check '{syncplan}' sync plan is not in '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer sync-plan info --name='" + syncplan + "' "
                    + "--organization='" + orgname + "') ]]; "
                    + "then hammer sync-plan delete "
                    + "--organization='" + orgname + "' "
                    + "--name='" + syncplan + "'; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove sync plan.",
        "sshkey": '',
        "shell": True
    }


def check_cv(orgname, cvname, cvdesc, options=""):
    """
    Creates the given content view in the given organization
    'orgname' is a str with the organization where the content view is created
    'cvname' is a str with the content view name
    'cvdesc' is a str with the content view description
    """
    return {
        "label": f"Check '{cvname}' content view for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer content-view list --organization='" + orgname + "'"
                    + "| grep '" + cvname + "') ]];"
                    + " then exit 0;"
                    + " else hammer content-view create --name='" + cvname + "'"
                    + " --label='" + cvname + "' --description='" + cvdesc + "'"
                    + " --organization='" + orgname + "'"
                    + " " + options + "; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot create the content view.",
        "sshkey": '',
        "shell": True
    }


def check_repo_cv(orgname, cvname, reponame):
    """
    Add the provided repo to the given content view
    'orgname' is a str with the organization where the content view is placed
    'cvname' is a str with the content view name
    'reponame' is a str with the repository name
    """
    return {
        "label": f"Check '{reponame}' repository to the '{cvname}' content view",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer content-view add-repository --name='" + cvname + "'"
                    + " --organization='" + orgname + "'"
                    + " --repository-id $(hammer --no-headers repository list"
                    + " --organization='" + orgname + "'"
                    + " --fields Id --name '" + reponame + "')",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot add the repository.",
        "sshkey": '',
        "shell": True
    }


def check_component_cv(orgname, cvname, component):
    """
    Add the provided repo to the given content view
    'orgname' is a str with the organization where the content view is placed
    'cvname' is a str with the content view name
    'reponame' is a str with the repository name
    """
    return {
        "label": f"Check '{component}' in '{cvname}' content view",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer --no-headers content-view component list"
                    + " --organization='" + orgname + "'"
                    + " --composite-content-view='" + cvname + "'"
                    + " --fields Name | grep '" + component + "') ]];"
                    + " then exit 0;"
                    + " else hammer content-view component add"
                    + " --component-content-view='" + component + "' --latest"
                    + " --composite-content-view='" + cvname + "'"
                    + " --organization='" + orgname + "'; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot add the repository.",
        "sshkey": '',
        "shell": True
    }


def check_publish_cv(orgname, cvname, cvdesc, lcname):
    """
    Publish the provided content view in the given organization
    'orgname' is a str with the organizationlt
    'cvname' is a str with the content view name
    'cvdesc' is a str with the content view description
    'lcname' is a str with the lifecycle name
    """
    return {
        "label": f"Check publish '{cvname}' content view in '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer content-view info --name='" + cvname + "'"
                    + " --organization='" + orgname + "'| grep '" + lcname + "') ]];"
                    + " then exit 0;"
                    + " else hammer content-view publish --name='" + cvname + "'"
                    + " --description='" + cvdesc + "'"
                    + " --organization='" + orgname + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot publish the content view.",
        "sshkey": '',
        "shell": True
    }


def check_promote_cv(orgname, cvname, cvdesc, lcname):
    """
    Publish the provided content view in the given organization
    'orgname' is a str with the organization
    'cvname' is a str with the content view name
    'cvdesc' is a str with the content view description
    'lcname' is a str with the lifecycle name
    """
    return {
        "label": f"Check content promotion in '{lcname}' lifecycle environment",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer content-view info --name='" + cvname + "'"
                    + " --organization='" + orgname + "'"
                    + " --fields 'Lifecycle environments/name' |"
                    + " grep '" + lcname + "') ]];"
                    + " then exit 0;"
                    + " else hammer content-view version promote"
                    + " --content-view='" + cvname + "'"
                    + " --to-lifecycle-environment='" + lcname + "'"
                    + " --description='" + cvdesc + "' --organization='"
                    + orgname + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot promote the content view.",
        "sshkey": '',
        "shell": True
    }


def remove_filter_cv(orgname, cvname, filter):
    """
    Removes the given filter in a content view from the given organization.
    'orgname' is a str with the organization where the content view is removed.
    'cvname' is a str with the content view name.
    'filter' is a str with the filter name.
    """
    return {
        "label": f"Remove '{filter}' filter in '{cvname}' content view from '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer --no-headers content-view filter list"
                    + " --organization='" + orgname + "'"
                    + " --content-view='" + cvname + "'"
                    + " --fields Name |"
                    + " grep '" + filter + "') ]]; then"
                    + " hammer content-view filter delete"
                    + " --organization='" + orgname + "'"
                    + " --content-view='" + cvname + "'"
                    + " --name='" + filter + "';"
                    + " fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the content view.",
        "sshkey": '',
        "shell": True
    }


def check_script(host, file):
    """
    """
    return {
        "label": f"Check '{file}' script in '{host[0]}'",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "chmod +x /root/" + file + ";"
                    + " sh /root/" + file + ";"
                    + " rm /root/" + file,
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot check the script.",
        "sshkey": '',
        "shell": True
    }


def remove_lifecycle_cv(orgname, cvname, lcname):
    """
    Removes the given lifecycle env from the given content view
    'orgname' is a str with the organization where the content view is removed
    'cvname' is a str with the content view name
    'lcname' is a str with the lifecycle name
    """
    return {
        "label": f"Remove '{lcname}' lifecycle environment from '{cvname}' content view",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer content-view info --name='" + cvname + "'"
                    + " --organization='" + orgname + "' | grep " + lcname + ") ]];"
                    + " then hammer content-view remove-from-environment"
                    + " --name='" + cvname + "'"
                    + " --organization='" + orgname + "'"
                    + " --lifecycle-environment='" + lcname + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the lifecycle environment.",
        "sshkey": '',
        "shell": True
    }


def remove_cv(orgname, cvname):
    """
    Removes the given content view from the given organization
    'orgname' is a str with the organization where the content view is removed
    'cvname' is a str with the content view name
    """
    return {
        "label": f"Remove '{cvname}' content view from '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer content-view list --organization='" + orgname + "'"
                    + "| grep '" + cvname + "') ]];"
                    + " then hammer content-view delete --name='" + cvname + "'"
                    + " --organization='" + orgname + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the content view.",
        "sshkey": '',
        "shell": True
    }


def check_host_cv(orgname, cvname, lcname, fqdn):
    """
    Update the host to the given content view from the given organization.
    'orgname' is a str with the organization where the content view is removed.
    'cvname' is a str with the content view name.
    'host' is a str with the host name.
    """
    return {
        "label": f"Check '{fqdn}' belongs to '{lcname}/{cvname}'",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer host list --organization='" + orgname + "'"
                    + " | grep '" + fqdn + "') ]];"
                    + " then hammer host update"
                    + " --name='" + fqdn + "'"
                    + " --organization='" + orgname + "'"
                    + " --lifecycle-environment='" + lcname + "'"
                    + " --content-view='" + cvname + "'; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot update the host.",
        "sshkey": '',
        "shell": True
    }


def check_repo_added(reponame, orgname, release):
    """
    Verifies if the given repo is enabled and if not, enables it in the given
    organization
    'orgname' is a str with the organization to enable the repo
    'repo' is a str with the repository name
    'release' is a str with the release version
    """
    return {
        "label": f"Check '{reponame}' repository in '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer repository-set list --organization='" + orgname + "'"
                    + " --enabled=yes | grep '" + reponame + "') ]];"
                    + " then exit 0;"
                    + " else hammer repository-set enable --name='" + reponame + "'"
                    + " --basearch='x86_64' --releasever='" + release + "' --organization='" + orgname + "';"
                    + " exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot enable the repository.",
        "sshkey": '',
        "shell": True
    }


def check_sync_repo(orgname, reponame, productname):
    """
    Synchronizes the repositories for the given product in the given organization
    'orgname' is a str with the organization to sync the repo
    'productname' is a str with the product name
    """
    return {
        "label": f"Check the '{reponame}' for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer repository info --name='" + reponame + "'"
                    + " --organization='" + orgname + "'"
                    + " --product='" + productname + "'"
                    + " | grep 'Status:.*Not Synced') ]];"
                    + " then hammer repository synchronize --name='" + reponame + "'"
                    + " --organization='" + orgname + "'"
                    + " --product='" + productname + "';"
                    + " else exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot synchronize the repository.",
        "sshkey": '',
        "shell": True
    }


def check_sync_product_repos(orgname, productname):
    """
    Synchronizes the repositories for the given product in the given organization
    'orgname' is a str with the organization to sync the repo
    'productname' is a str with the product name
    """
    return {
        "label": f"Check the '{productname}' product for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer product synchronize"
                    + " --name '" + productname + "'"
                    + " --organization '" + orgname + "'",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot synchronize the product.",
        "sshkey": '',
        "shell": True
    }


def check_lifecycle(orgname, lcname, lcdesc, lcprior):
    """
    Creates the given lifecycle in the given organization
    'orgname' is a str with the organization to create the lifecycle
    'lcname' is a str with the lifecycle name
    'lcdesc' is a str with the lifecycle description
    'lcprior' is a str with the previous lifecycle name
    """
    return {
        "label": f"Check '{lcname}' lifecycle for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer lifecycle-environment info --name='" + lcname + "'"
                    + " --organization='" + orgname + "') ]];"
                    + " then exit 0;"
                    + " else hammer lifecycle-environment create --name='" + lcname + "'"
                    + " --description='" + lcdesc + "' --prior='" + lcprior + "'"
                    + " --organization='" + orgname + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot create the lifecycle-environment.",
        "sshkey": '',
        "shell": True
    }


def remove_lifecycle(orgname, lcname):
    """
    Removes the given lifecycle in the given organization
    'orgname' is a str with the organization to create the lifecycle
    'lcname' is a str with the product name
    """
    return {
        "label": f"Remove '{lcname}' lifecycle for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer lifecycle-environment info --name='" + lcname + "'"
                    + " --organization='" + orgname + "') ]];"
                    + " then hammer lifecycle-environment delete --name='" + lcname + "'"
                    + " --organization='" + orgname + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the lifecycle-environment.",
        "sshkey": '',
        "shell": True
    }


def register_host(host, orgname, environment):
    """
    Register the provided hostname
    'host' should be passed in as a list
    'orgname' is a str with the organization where the host is included
    'environment' is a str with the environment name
    'options' is a str with the additional options
    """
    return {
        "label": f"Check register '{host[0]}'",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(subscription-manager status | grep 'This host has access to content') ]];"
                    + " then exit 0;"
                    + " else subscription-manager clean;"
                    + " yum -y localinstall http://satellite.lab.example.com/pub/katello-ca-consumer-latest.noarch.rpm;"
                    + " subscription-manager register --org='" + orgname + "'"
                    + " --environment='" + environment + "'"
                    + " --username='admin' --password='redhat'" + "; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot register the host.",
        "sshkey": '',
        "shell": True
    }


def check_packages(host, packages, options=""):
    """
    Install a list of packages using yum.
    'host' should be passed in as a list.
    'packages' is a str with the packages to be installed.
    'options' is a str with the additional options.
    """
    return {
        "label": f"Check the '{packages}' package(s)",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "yum install -y " + options + " "
                    + packages,
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot install the package(s).",
        "sshkey": '',
        "shell": True
    }


def check_yum_module(host, modules, options=""):
    """
    Enable a list of modules using yum.
    'host' should be passed in as a list.
    'modules' is a str with the modules to be enabled.
    'options' is a str with the additional options.
    """
    return {
        "label": f"Check the '{modules}' module(s)",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "yum module enable -y " + options + " "
                    + modules,
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot enable the module(s).",
        "sshkey": '',
        "shell": True
    }


def unregister_host(host):
    """
    Unregister the provided hostname
    'host' should be passed in as a list
    """
    return {
        "label": f"Unregister '{host[0]}'",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(subscription-manager status | grep 'Unknown') ]];"
                    + "then exit 0;"
                    + " else subscription-manager unregister;"
                    + " subscription-manager clean;"
                    + " yum -y remove katello-ca-consumer-satellite.lab.example.com.noarch;"
                    + " yum clean all; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot unregister the host.",
        "sshkey": '',
        "shell": True
    }


def remove_host(orgname, hostfqdn):
    """
    Unregister the provided hostfqdn
    'orgname' is a str with the organization from where the host is removed
    'hostname' is a str with the host fqdn
    """
    return {
        "label": f"Remove '{hostfqdn}' from '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer host list --organization='" + orgname + "'"
                    + " | grep '" + hostfqdn + "') ]];"
                    + " then hammer host update --managed='false' --name='" + hostfqdn + "'"
                    + " --organization='" + orgname + "';"
                    + " hammer host delete --name='" + hostfqdn + "'"
                    + " --organization='" + orgname + "'; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the host.",
        "sshkey": '',
        "shell": True
    }


def remove_packages(host, packages, options=""):
    """
    Remove a list of packages using yum.
    'host' should be passed in as a list.
    'packages' is a str with the packages to be installed.
    'options' is a str with the additional options.
    """
    return {
        "label": f"Remove the '{packages}' package(s)",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "yum remove -y " + options + " "
                    + packages,
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the package(s).",
        "sshkey": '',
        "shell": True
    }


def check_activation_key(orgname, cvname, lcname, keyname, options=""):
    """
    Create the activation key for the given organization
    'orgname' is a str with the organization
    'cvname' is a str with the content view name
    'lcname' is a str with the lifecycle name
    'keyname' is a str with the key name
    'options' is a str with other options for the key creation
    """
    return {
        "label": f"Check '{keyname}' activation key for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer activation-key list --name='" + keyname + "'"
                    + " --organization='" + orgname + "' | grep '" + keyname + "') ]];"
                    + " then exit 0;"
                    + " else hammer activation-key create"
                    + " --organization='" + orgname + "'"
                    + " --content-view='" + cvname + "'"
                    + " --lifecycle-environment='" + lcname + "'"
                    + " --name='" + keyname + "' "
                    + options + "; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot create the activation key.",
        "sshkey": '',
        "shell": True
    }


def remove_activation_key(orgname, keyname):
    """
    Remove the activation key for the given organization
    'orgname' is a str with the organization
    'keyname' is a str with the key name
    """
    return {
        "label": f"Remove '{keyname}' activation key for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer activation-key list --name='" + keyname + "'"
                    + " --organization='" + orgname + "' | grep '" + keyname + "') ]];"
                    + " then hammer activation-key delete"
                    + " --organization='" + orgname + "'"
                    + " --name='" + keyname + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the activation key.",
        "sshkey": '',
        "shell": True
    }


def check_key_override(orgname, keyname, options=""):
    """
    Create the activation key for the given organization
    'orgname' is a str with the organization
    'keyname' is a str with the key name
    'options' is a str with options for the key override
    """
    return {
        "label": f"Override '{keyname}' activation key",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer activation-key content-override --name='" + keyname + "'"
                    + " --organization='" + orgname + "' " + options,
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot override the activation key.",
        "sshkey": '',
        "shell": True
    }


def check_bootstrap_capsule(orgname, keyname):
    """
    Check Capsule server registration.
    'orgname' is a str with the organization.
    'keyname' is a str with the key name.
    """
    return {
        "label": "Check Capsule server registration",
        "task": tasks.run_command,
        "hosts": ["capsule"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(subscription-manager status"
                    + " | grep 'This host has access to content') ]];"
                    + " then exit 0;"
                    + " else wget -O bootstrap.py"
                    + " http://satellite.lab.example.com/pub/bootstrap.py;"
                    + " subscription-manager clean;"
                    + " python3 bootstrap.py"
                    + " --login=admin"
                    + " --server=satellite.lab.example.com"
                    + " --organization='" + orgname + "'"
                    + " --location='Default Location'"
                    + " --activationkey='" + keyname + "'"
                    + " --skip foreman"
                    + " --force;"
                    + " fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot bootstrap capsule server.",
        "sshkey": '',
        "shell": True
    }


def check_capsule_install():
    """
    Install Capsule server.
    'orgname' is a str with the organization.
    'keyname' is a str with the key name.
    """
    return {
        "label": "Check Capsule server installation",
        "task": tasks.run_command,
        "hosts": ["localhost"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(ssh root@satellite \"hammer capsule list |"
                    + " grep capsule.lab.example.com\") ]];"
                    + " then scp -r root@satellite:/root/capsule_cert /home/student/;"
                    + " scp -r /home/student/capsule_cert root@capsule:~;"
                    + " else scp -r root@satellite:/root/capsule_cert /home/student/;"
                    + " scp -r /home/student/capsule_cert root@capsule:~;"
                    + " ssh root@capsule \"satellite-installer --scenario capsule"
                    + " --certs-tar-file '/root/capsule_cert/capsule_certs.tar'"
                    + " --foreman-proxy-register-in-foreman 'true'"
                    + " --foreman-proxy-foreman-base-url 'https://satellite.lab.example.com'"
                    + " --foreman-proxy-trusted-hosts 'satellite.lab.example.com'"
                    + " --foreman-proxy-trusted-hosts 'capsule.lab.example.com'"
                    + " --foreman-proxy-oauth-consumer-key"
                    + " $(grep foreman-proxy-oauth-consumer-key /home/student/capsule_cert/capsule_cert_output.txt | cut -d '\"' -f2)"
                    + " --foreman-proxy-oauth-consumer-secret"
                    + " $(grep foreman-proxy-oauth-consumer-secret /home/student/capsule_cert/capsule_cert_output.txt | cut -d '\"' -f2)"
                    + " --puppet-server-foreman-url 'https://satellite.lab.example.com'\"; fi;"
                    + " rm -rf /home/student/capsule_cert;"
                    + " ssh root@satellite \"rm -rf /root/capsule_cert\"",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot install capsule server.",
        "sshkey": '',
        "shell": True
    }


def check_capsule_certs(capsule_fqdn):
    """
    Create the Capsule certificates.
    """
    return {
        "label": "Check Capsule certificate files",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "rm -rf /root/capsule_cert;"
                    + " mkdir /root/capsule_cert;"
                    + " capsule-certs-generate"
                    + " --foreman-proxy-fqdn " + capsule_fqdn
                    + " --certs-tar /root/capsule_cert/capsule_certs.tar"
                    + " > /root/capsule_cert/capsule_cert_output.txt"
                    + " 2>/dev/null",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot bootstrap capsule server.",
        "sshkey": '',
        "shell": True
    }


def remove_capsule(capsule_fqdn):
    """
    Remove Capsule Server.
    'capsule_fqdn' is a str with the capsule fqdn.
    """
    return {
        "label": f"Remove '{capsule_fqdn}' capsule server",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer capsule list | grep '" + capsule_fqdn + "') ]];"
                    + " then hammer capsule delete"
                    + " --name='" + capsule_fqdn + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the capsule server.",
        "sshkey": '',
        "shell": True
    }


def remove_capsule_ansible():
    """
    Disable Ansible service in the Capsule Server.
    """
    return {
        "label": "Disable Ansible service in the Capsule Server.",
        "task": tasks.run_command,
        "hosts": ["localhost"],
        "command": "if [[ $(ssh root@satellite"
                   + " \"hammer capsule info"
                   + " --name capsule.lab.example.com"
                   + " --fields Features/name |"
                   + " grep Ansible\") ]];"
                   + " then ssh root@capsule"
                   + " \"rm -f /etc/foreman-proxy/settings.d/ansible.yml;"
                   + " satellite-maintain service restart\"; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot disable Ansible service.",
        "sshkey": '',
        "shell": True
    }


def remove_capsule_lc(capsule_fqdn, orgname, lcname):
    """
    Remove lifecycle environments from the capsule.
    'capsule' is a str with the capsule fqdn name.
    'orgname' is a str with the organization.
    'lcname' is a str with the lifecycle name.
    """
    return {
        "label": f"Remove the '{lcname}' lifecycle environment from the capsule.",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer --no-headers capsule content"
                    + " lifecycle-environments"
                    + " --name " + capsule_fqdn + " |"
                    + " grep " + lcname + ") ]];"
                    + " then hammer capsule content"
                    + " remove-lifecycle-environment"
                    + " --lifecycle-environment='" + lcname + "'"
                    + " --organization='" + orgname + "'"
                    + " --id=$(hammer capsule info"
                    + " --name='" + capsule_fqdn + "'"
                    + " --fields=Id | grep Id | awk '{ print $2 }');"
                    + " hammer capsule content synchronize"
                    + " --id=$(hammer capsule info"
                    + " --name='" + capsule_fqdn + "'"
                    + " --fields=Id | grep Id | awk '{ print $2 }');"
                    + " fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove lifecycle from capsule.",
        "sshkey": '',
        "shell": True
    }


def verify_capsule(capsule_fqdn):
    """
    Verify if the capsule is installed.
    'capsule' is a str with the capsule fqdn name.
    """
    return {
        "label": f"Verify the '{capsule_fqdn}' capsule is installed.",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer capsule info --name "
                    + capsule_fqdn,
        "returns": 0,
        "prints": capsule_fqdn,
        "options": [],
        "fatal": True,
        "student_msg": "Capsule is not installed.",
        "sshkey": '',
        "shell": True
    }


def check_capsule_org_loc(capsule, organizations, locations):
    """
    Update the capsule organizations and locations.
    'capsule' is a str with the capsule name
    'orgname' is a str with the organization
    'location' is a str with the location name
    """
    return {
        "label": f"Check '{capsule}' to '{organizations}' organization and '{locations}' location",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer capsule update"
                    + " --name " + capsule
                    + " --organizations='" + organizations + "'"
                    + " --locations='" + locations + "'",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot update capsule locations and organizations.",
        "sshkey": '',
        "shell": True
    }


def remove_puppet_ca(hostfqdn):
    """
    Revoke Puppet certificate.
    'hostfqdn' is a str with the host fqdn
    """
    return {
        "label": f"Revoke Puppet certificate in '{hostfqdn}'.",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(puppetserver ca list --all |"
                   + " grep '" + hostfqdn + "') ]];"
                   + " then puppetserver ca revoke"
                   + " --certname " + hostfqdn + ";"
                   + " puppetserver ca clean"
                   + " --certname " + hostfqdn
                   + " ; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot revoke Puppet certificate.",
        "sshkey": '',
        "shell": True
    }


def remove_capsule_puppet_service(host):
    """
    Disable Puppet service in the Satellite or Capsule Server.
    'host' should be passed in as a list.
    """
    return {
        "label": f"Disable Puppet service in the '{host[0]}' Server.",
        "task": tasks.run_command,
        "hosts": ["localhost"],
        "command": "if [[ $(ssh root@satellite"
                   + " \"hammer capsule info"
                   + " --name " + host[0] + ".lab.example.com"
                   + " --fields Features/name |"
                   + " grep Puppet\") ]];"
                   + " then ssh root@" + host[0]
                   + " \"satellite-maintain"
                   + " plugin purge-puppet\"; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot disable Puppet service.",
        "sshkey": '',
        "shell": True
    }


def remove_file_directory(host, filedir):
    """
    Remove file or directory.
    'filedir' is a str with the file or directory name.
    """
    return {
        "label": f"Remove '{filedir}' file/directory in '{host[0]}'",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "rm -rf " + filedir,
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the file or directory.",
        "sshkey": '',
        "shell": True
    }


def check_foreman_key(host, client):
    """
    Copy the Foreman SSH Keys for Remote Execution.
    'host' is the host to read the sshkey,
           and it should be passed in as a list.
    'client' is the hostname to be checked.
           and it should be passed in as a list.
    """
    return {
        "label": f"Check the '{host[0]}' Foreman SSH Key for remote execution in '{client[0]}'.",
        "task": tasks.run_command,
        "hosts": ["localhost"],
        "command": "if [[ $(ssh root@" + host[0]
                   + " 'ssh -i ~foreman-proxy/.ssh/id_rsa_foreman_proxy"
                   + " -o 'StrictHostKeyChecking=no' -o 'PasswordAuthentication=no'"
                   + " root@" + client[0] + " hostname') ]];"
                   + " then exit 0;"
                   + " else scp root@" + host[0]
                   + ":/usr/share/foreman-proxy/.ssh/id_rsa_foreman_proxy.pub"
                   + " /tmp/" + host[0] + "_id_rsa_foreman_proxy.pub;"
                   + " scp /tmp/" + host[0] + "_id_rsa_foreman_proxy.pub"
                   + " root@" + client[0] + ":/tmp/;"
                   + " ssh root@" + client[0]
                   + " 'cat /tmp/" + host[0] + "_id_rsa_foreman_proxy.pub"
                   + " >> .ssh/authorized_keys';"
                   + " ssh root@" + client[0] + " 'chmod 600 /root/.ssh/authorized_keys';"
                   + " ssh root@" + client[0] + " 'rm -rf /tmp/" + host[0] + "_id_rsa_foreman_proxy.pub';"
                   + " fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot copy the sshkey.",
        "sshkey": '',
        "shell": True
    }


def remove_foreman_key(host, client):
    """
    Remove the Foreman SSH Keys for Remote Execution.
    'host' is the host to read the sshkey,
           and it should be passed in as a list.
    'client' is the hostname to be checked.
           and it should be passed in as a list.
    """
    return {
        "label": f"Remove the '{host[0]}' Foreman SSH Key for remote execution in '{client[0]}'.",
        "task": tasks.run_command,
        "hosts": client,
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(grep foreman-proxy@" + host[0]
                    + ".lab.example.com"
                    + " .ssh/authorized_keys) ]];"
                    + " then sed -i '/foreman-proxy@"
                    + host[0] + ".lab.example.com/d' .ssh/authorized_keys;"
                    + " fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the sshkey.",
        "sshkey": '',
        "shell": True
    }


def check_ports(host, ports):
    """
    Open the given ports.
    'host' should be passed in as a list.
    'ports' is a str with the ports separated by a blank space (8080/tcp).
    """
    return {
        "label": f"Check the '{ports}' port(s) in '{host[0]}'",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "for I in " + ports + ";"
                    + " do firewall-cmd"
                    + " --add-port=$I"
                    + " --permanent;"
                    + " done;"
                    + " firewall-cmd --reload",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot open ports on the host.",
        "sshkey": '',
        "shell": True
    }


def remove_ports(host, ports):
    """
    Open the given ports.
    'host' should be passed in as a list.
    'ports' is a str with the ports separated by a blank space (8080/tcp).
    """
    return {
        "label": f"Remove the '{ports}' port(s) in '{host[0]}'",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "for I in " + ports + ";"
                    + " do firewall-cmd"
                    + " --remove-port=$I"
                    + " --permanent;"
                    + " done;"
                    + " firewall-cmd --reload",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove ports on the host.",
        "sshkey": '',
        "shell": True
    }


def remove_content_credential(orgname, credname):
    """
    Remove the content credential for the given organization
    'orgname' is a str with the organization
    'credname' is a str with the content credential name
    """
    return {
        "label": f"Remove '{credname}' content credential for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer content-credentials list"
                    + " --organization='" + orgname + "' | grep '" + credname + "') ]];"
                    + " then hammer content-credentials delete"
                    + " --organization='" + orgname + "'"
                    + " --name='" + credname + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the content credential.",
        "sshkey": '',
        "shell": True
    }


def copy_file(host, file, dest):
    """
    Copy a file from workstation to a host.
    'host' is a str with the hostname to copy the file.
    'file' is a str with the path.
    'dest' is a str with the path to copy the file.
    """
    return {
        "label": f"Copy file in '{host}':'{dest}'",
        "task": tasks.run_command,
        "hosts": ["localhost"],
        "command": "if  [[ " + host + " == 'localhost' ]] ||"
                   + " [[ " + host + " == 'workstation' ]];"
                   + " then cp " + file
                   + " " + dest + ";"
                   + " else scp " + file
                   + " root@" + host + ":" + dest
                   + "; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot copy the file.",
        "sshkey": '',
        "shell": True
    }


def check_root_ssh_login(host):
    """
    Enable SSH root login.
    'host' should be passed in as a list.
    """
    return {
        "label": f"Enable '{host[0]}' SSH root login",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "sed -i 's/#PermitRootLogin"
                    + " prohibit-password/PermitRootLogin yes/'"
                    + " /etc/ssh/sshd_config;"
                    + " systemctl restart sshd",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot enable SSH root login.",
        "sshkey": '',
        "shell": True
    }


def remove_root_ssh_login(host):
    """
    Enable SSH root login.
    'host' should be passed in as a list.
    """
    return {
        "label": f"Remove '{host[0]}' SSH root login",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "sed -i 's/PermitRootLogin"
                    + " yes/#PermitRootLogin prohibit-password/'"
                    + " /etc/ssh/sshd_config;"
                    + " systemctl restart sshd",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot disable SSH root login.",
        "sshkey": '',
        "shell": True
    }


def remove_job_template(jobtemplate):
    """
    Remove job template from Satellite.
    'jobtemplate' is a str with the job template name.
    """
    return {
        "label": f"Remove '{jobtemplate}' job template",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer job-template list |"
                    + " grep '" + jobtemplate + "') ]];"
                    + " then hammer job-template delete "
                    + " --name='" + jobtemplate + "';"
                    + " fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the job template.",
        "sshkey": '',
        "shell": True
    }


def remove_ssh_banner(host):
    """
    Remove SSH banner.
    'host' should be passed in as a list.
    """
    return {
        "label": f"Remove SSH Banner in '{host[0]}'",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "sed -i 's,Banner /etc/issue,#Banner none,'"
                    + " /etc/ssh/sshd_config;"
                    + " systemctl restart sshd",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the SSH banner.",
        "sshkey": '',
        "shell": True
    }


def remove_ansible_variable(orgname, variable):
    """
    Remove an Ansible variable from Satellite.
    'orgname' is a str with the organization
    'variable' is a str with the Ansible variable name.
    """
    return {
        "label": f"Remove '{variable}' Ansible variable",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer ansible variables list |"
                    + " grep " + variable + ") ]];"
                    + " then hammer ansible variables delete"
                    + " --name " + variable
                    + " --organization='" + orgname + "';"
                    + " fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the Ansible variable.",
        "sshkey": '',
        "shell": True
    }


def remove_ansible_role(orgname, role):
    """
    Remove an Ansible role from Satellite.
    'orgname' is a str with the organization
    'role' is a str with the Ansible variable name.
    """
    return {
        "label": f"Remove '{role}' Ansible role",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer ansible roles list |"
                    + " grep " + role + ") ]];"
                    + " then hammer ansible roles delete"
                    + " --name " + role
                    + " --organization='" + orgname + "';"
                    + " fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the Ansible role.",
        "sshkey": '',
        "shell": True
    }


def remove_user(keyname):
    """
    Remove a user
    'keyname' is a str with the key name
    """
    return {
        "label": f"Remove '{keyname}' user",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer user list --search '" + keyname + "'"
                    + " --fields Login | grep '" + keyname + "') ]];"
                    + " then hammer user delete"
                    + " --login '" + keyname + "'"
                    + " ; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the user.",
        "sshkey": '',
        "shell": True
    }


def remove_role(keyname):
    """
    Remove a role
    'keyname' is a str with the key name
    """
    return {
        "label": f"Remove '{keyname}' role",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer role info --name '" + keyname + "') ]];"
                    + " then hammer role delete --name '" + keyname + "'"
                    + " ;fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the role.",
        "sshkey": '',
        "shell": True
    }


def check_user_description(user, description):
    """
    Update a user description
    'user' is a str with the user login.
    'description' is a str with the new description
    """
    return {
        "label": f"Check the description for the '{user}' user",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer user update"
                    + " --login='" + user + "'"
                    + " --description='" + description + "'",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot update the description.",
        "sshkey": '',
        "shell": True
    }


def check_download_policy(orgname, repo, policy):
    """
    Change the Download policy
    'orgname' is a str with the organization.
    'repo' is a str with the repository.
    'policy' is a str with the download policy.
    """
    return {
        "label": f"Check Download policy for the '{repo}' repo",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer repository update --id"
                    + " $(hammer --no-headers repository list"
                    + " --organization '" + orgname + "'"
                    + " --name '" + repo + "' --fields Id)"
                    + " --download-policy '" + policy + "'"
                    + " --organization '" + orgname + "'",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot update the download policy.",
        "sshkey": '',
        "shell": True
    }


def check_all_hosts_cv(orgname, from_cv, to_cv, to_lc):
    """
    Change all the hosts in the provided organization to a different
    content view and to a different lifecycle environment.
    'orgname' is a str with the organization.
    'from_cv' is a str with the content view to which the host belongs.
    'to_cv' is a str with the content view the host will move to.
    'to_lc' is a str with the lifecycle environment the host will move to.
    """
    return {
        "label": f"Check all hosts in the '{from_cv}' CV",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "for HOST in $(hammer host list"
                    + " --organization '" + orgname + "'"
                    + " --fields Name,'Content view'"
                    + " | grep '" + from_cv + "'"
                    + " | awk '{ print $1 }'); do"
                    + " hammer host update"
                    + " --lifecycle-environment '" + to_lc + "'"
                    + " --content-view '" + to_cv + "'"
                    + " --organization " + orgname
                    + " --name $HOST; done",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot move the hosts to the CV.",
        "sshkey": '',
        "shell": True
    }


def remove_all_cvs(orgname):
    """
    Remove all the Content Views and their content.
    Host are moved to the 'Default Organization View' CV.
    'orgname' is a str with the organization.
    """
    return {
        "label": f"Remove Content Views in '{orgname}'",
        "task": tasks.run_command,
        "hosts": ["workstation"],
        "command": "scp /home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/remove_cvs.sh"
                   + " root@satellite:/root/;"
                   + " ssh root@satellite \"chmod +x /root/remove_cvs.sh;"
                   + " sh /root/remove_cvs.sh " + orgname + ";"
                   + " rm /root/remove_cvs.sh\"",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove CVs in the organization.",
        "sshkey": '',
        "shell": True
    }


def check_cvs_in_place(orgname, contentview):
    """
    Check the Content View and their content.
    if something is not in place, it publish and promote new versions.
    'orgname' is a str with the organization.
    'contentview' is a str with the content view.
    """
    return {
        "label": f"Check '{contentview}' content view in '{orgname}'",
        "task": tasks.run_command,
        "hosts": ["workstation"],
        "command": "scp /home/student/.venv/labs/lib/python3.9/site-packages/rh403/materials/labs/check_cvs.sh"
                   + " root@satellite:/root/;"
                   + " ssh root@satellite \"chmod +x /root/check_cvs.sh;"
                   + " sh /root/check_cvs.sh " + orgname + " " + contentview + ";"
                   + " rm /root/check_cvs.sh\"",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot check CVs in the organization.",
        "sshkey": '',
        "shell": True
    }


def create_domain(loc_domain, domain, orgname):
    """
    Add a domain.
    'loc_domain' is a str with the location name of the domain.
    'domain' is a str with the domain name.
    'orgname' is a str with the organization.
    """
    return {
        "label": f"Create '{loc_domain}' domain",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer domain list"
                    + " | grep '" + domain + "') ]];"
                    + " then exit 0;"
                    + " else hammer domain create"
                    + " --organization='" + orgname + "'"
                    + " --name='" + domain + "'; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot create the domain.",
        "sshkey": '',
        "shell": True
    }


def check_capsule_domain(loc_domain, domain, orgname, capsule):
    """
    Configure a domain in a capsule.
    'loc_domain' is a str with the location name of the domain.
    'domain' is a str with the domain name.
    'orgname' is a str with the organization.
    'capsule' is a str with the fqdn of a capsule.
    """
    return {
        "label": f"Configure '{loc_domain}' domain",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer domain list"
                    + " | grep '" + domain + "') ]];"
                    + " then hammer domain update"
                    + " --organizations='" + orgname + "'"
                    + " --locations='" + loc_domain + "'"
                    + " --name='" + domain + "'"
                    + " --dns='" + capsule + "'; else exit 1; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot configure the domain.",
        "sshkey": '',
        "shell": True
    }


def remove_hostgroup(hostgroup):
    """
    Remove a host group.
    'hostgroup' is a str with the host group name.
    """
    return {
        "label": f"Remove the '{hostgroup}' host group",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer hostgroup list"
                    + " | grep '" + hostgroup + "') ]];"
                    + " then hammer hostgroup delete"
                    + " --name='" + hostgroup + "'; fi;",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the host group.",
        "sshkey": '',
        "shell": True
    }


def remove_subnet(domain, subnet):
    """
    Remove a subnet.
    'domain' is a str with the domain name.
    'hostgroup' is a str with the subnet name.
    """
    return {
        "label": f"Remove the '{subnet}' subnet",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer subnet list"
                    + " | grep '" + subnet + "') ]];"
                    + " then if [[ $(hammer subnet info"
                    + " --name='" + subnet + "'"
                    + " | grep '" + domain + "') ]];"
                    + " then hammer subnet update"
                    + " --name='" + subnet + "'"
                    + " --domains ''; fi;"
                    + " hammer subnet delete"
                    + " --name='" + subnet + "'; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the subnet.",
        "sshkey": '',
        "shell": True
    }


def remove_domain(domain):
    """
    Remove a domain.
    'hostgroup' is a str with the domain name.
    """
    return {
        "label": f"Remove the '{domain}' domain",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer domain list"
                    + " | grep '" + domain + "') ]];"
                    + " then hammer domain delete"
                    + " --name='" + domain + "'; fi;",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the domain.",
        "sshkey": '',
        "shell": True
    }


def check_directory(host, dir):
    """
    create a directory.
    'host' should be passed in as a list
    'dir' is a str with the directory name.
    """
    return {
        "label": f"Check the '{dir}' directory",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": f"""
            if ! [[ -d {dir} ]]; \
                then mkdir -p {dir}; \
            fi
            """,
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot check the directory.",
        "sshkey": '',
        "shell": True
    }
