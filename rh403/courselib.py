"""
RH403 course library

To use these functions, add an import statement to your lab scripts:
from . import courselib

"""

from labs.common import tasks


def satellite_status():
    """
    Verifies the satellite server status.
    Fails if the satellite status is not OK.
    """
    return {
        "label": "Check Satellite status",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "satellite-maintain service status",
        "returns": 0,
        "prints": "OK",
        "options": [],
        "fatal": False,
        "student_msg": "Run 'satellite-maintain service restart' in satellite machine.",
        "sshkey": '',
        "shell": True
    }


def create_org(host, orgname, orgdesc):
    """
    Creates the organization given as parameter.
    'host' should be passed in as a list
    'orgname' is a str with the organization name to be created
    'orgdesc' is a str with the organization description
    """
    return {
        "label": f"Verify '{orgname}' organization exists",
        "task": tasks.run_command,
        "hosts": host,
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


def remove_org(host, orgname):
    """
    Removes the organization given as parameter.
    'host' should be passed in as a list
    'orgname' is a str with the organization name to be removed
    """
    return {
        "label": f"Remove '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": host,
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


def create_loc(host, locname, orgname):
    """
    Creates the location given as parameter inside the organization.
    'host' should be passed in as a list
    'locname' is a str with the location name to be created
    'orgname' is a str with the organization where the location will be created
    """
    return {
        "label": f"Verify '{locname}' location exists inside '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": host,
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


def remove_loc(host, locname):
    """
    Removes the location given as parameter inside the organization.
    'host' should be passed in as a list
    'locname' is a str with the location name to be removed
    """
    return {
        "label": f"Remove '{locname}' location",
        "task": tasks.run_command,
        "hosts": host,
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


def check_manifest(host, orgname, manifest):
    """
    Verifies if the manifest exists in the organization, and if not it
    downloads if from the repo url and installs it.
    'host' should be passed in as a list
    'orgname' is a str with the organization to place the manifest
    'manifest' is a str with the manifest path name
    """
    return {
        "label": f"Check manifest in '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer subscription list --organization='" + orgname + "'"
                    + " | grep 'Red Hat Enterprise Linux Server, Standard (Physical or Virtual Nodes)') ]];"
                    + " then exit 0;"
                    + " else if [[ -f " + manifest + " ]];"
                    + " then hammer organization update --name='" + orgname + "' --redhat-repository-url=http://cdn.lab.example.com "
                    + " && hammer subscription upload --file='" + manifest + "' --organization='"
                    + orgname + "'; exit 0; fi; exit 1; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot import the manifest.",
        "sshkey": '',
        "shell": True
    }


def check_repo(host, reponame, orgname, release):
    """
    Verifies if the given repo is enabled and if not, enables it in the given
    organization
    'host' should be passed in as a list
    'orgname' is a str with the organization to enable the repo
    'repo' is a str with the repository name
    'release' is a str with the release version
    """
    return {
        "label": f"Check '{reponame}' repository in '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": host,
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


def sync_repo(host, orgname, reponame, productname):
    """
    Synchronizes the repositories for the given product in the given organization
    'host' should be passed in as a list
    'orgname' is a str with the organization to sync the repo
    'productname' is a str with the product name
    """
    return {
        "label": f"Sync '{reponame}' for '{orgname}' organization (it will take long the first time)",
        "task": tasks.run_command,
        "hosts": host,
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


def check_lifecycle(host, orgname, lcname, lcdesc, lcprior):
    """
    Creates the given lifecycle in the given organization
    'host' should be passed in as a list
    'orgname' is a str with the organization to create the lifecycle
    'lcname' is a str with the lifecycle name
    'lcdesc' is a str with the lifecycle description
    'lcprior' is a str with the previous lifecycle name
    """
    return {
        "label": f"Check '{lcname}' lifecycle for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": host,
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


def remove_lifecycle(host, orgname, lcname):
    """
    Removes the given lifecycle in the given organization
    'host' should be passed in as a list
    'orgname' is a str with the organization to create the lifecycle
    'lcname' is a str with the product name
    """
    return {
        "label": f"Remove '{lcname}' lifecycle for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": host,
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


def create_cv(host, orgname, cvname, cvdesc):
    """
    Creates the given content view in the given organization
    'host' should be passed in as a list
    'orgname' is a str with the organization where the content view is created
    'cvname' is a str with the content view name
    'cvdesc' is a str with the content view description
    """
    return {
        "label": f"Configure '{cvname}' content view for '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer content-view list --organization='" + orgname + "'"
                    + "| grep '" + cvname + "') ]];"
                    + " then exit 0;"
                    + " else hammer content-view create --name='" + cvname + "'"
                    + " --label='" + cvname + "' --description='" + cvdesc + "'"
                    + " --organization='" + orgname + "'; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot create the content view.",
        "sshkey": '',
        "shell": True
    }


def remove_cv(host, orgname, cvname):
    """
    Removes the given content view from the given organization
    'host' should be passed in as a list
    'orgname' is a str with the organization where the content view is removed
    'cvname' is a str with the content view name
    """
    return {
        "label": f"Remove '{cvname}' content view from '{orgname}' organization",
        "task": tasks.run_command,
        "hosts": host,
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


def remove_lifecycle_env(host, orgname, cvname, lcname):
    """
    Removes the given lifecycle env from the given content view
    'host' should be passed in as a list
    'orgname' is a str with the organization where the content view is removed
    'cvname' is a str with the content view name
    'lcname' is a str with the lifecycle name
    """
    return {
        "label": f"Remove '{lcname}' lifecycle environment from '{cvname}' content view",
        "task": tasks.run_command,
        "hosts": host,
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


def addrepo_cv(host, orgname, cvname, reponame):
    """
    Add the provided repo to the given content view
    'host' should be passed in as a list
    'orgname' is a str with the organization where the content view is placed
    'cvname' is a str with the content view name
    'reponame' is a str with the repository name
    """
    return {
        "label": f"Adding '{reponame}' repository to the '{cvname}' content view",
        "task": tasks.run_command,
        "hosts": host,
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


def register_host(host, orgname, environment, options=""):
    """
    Register the provided hostname
    'host' should be passed in as a list
    'orgname' is a str with the organization where the host is included
    'environment' is a str with the environment name
    'options' is a str with the additional options
    """
    return {
        "label": f"Register '{host[0]}'",
        "task": tasks.run_command,
        "hosts": host,
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(subscription-manager status | grep 'This host has access to content') ]];"
                    + " then exit 0;"
                    + " else subscription-manager clean;"
                    + " yum -y localinstall http://satellite.lab.example.com/pub/katello-ca-consumer-latest.noarch.rpm;"
                    + " subscription-manager register --org='" + orgname + "'"
                    + " --environment='" + environment + "' " + options + "; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot register the host.",
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
        "command": "subscription-manager remove --all;"
                    + " subscription-manager unregister;"
                    + " subscription-manager clean;"
                    + " yum -y remove katello-ca-consumer-satellite.lab.example.com katello-agent;"
                    + " rm -f /etc/gofer/plugins/katello.conf;"
                    + " yum clean all &",
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
                    + " then hammer host delete --name='" + hostfqdn + "'"
                    + " --organization='" + orgname + "'; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the host.",
        "sshkey": '',
        "shell": True
    }


def set_default(orgname, locname):
    """
    Set the default login to the given organization and location names
    'orgname' is a str with the organization to be the default
    'locname' is a str with the location to be the default
    """
    return {
        "label": f"Set login default to '{orgname}' and '{locname}'",
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


def content_publish(orgname, cvname, cvdesc, lcname):
    """
    Publish the provided content view in the given organization
    'orgname' is a str with the organizationlt
    'cvname' is a str with the content view name
    'cvdesc' is a str with the content view description
    'lcname' is a str with the lifecycle name
    """
    return {
        "label": f"Publish '{cvname}' content view in '{orgname}' organization",
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


def promote_cv(orgname, cvname, cvdesc, lcname):
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


def create_key(orgname, cvname, lcname, keyname, options=""):
    """
    Create the activation key for the given organization
    'orgname' is a str with the organization
    'cvname' is a str with the content view name
    'lcname' is a str with the lifecycle name
    'keyname' is a str with the key name
    'options' is a str with other options for the key creation
    """
    return {
        "label": f"Create '{keyname}' activation key for '{orgname}' organization",
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


def remove_key(orgname, keyname):
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


def key_override(orgname, keyname, options=""):
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


def key_addcoll(orgname, keyname, collection):
    """
    Create the activation key for the given organization
    'orgname' is a str with the organization
    'keyname' is a str with the key name
    'collection' is a str with the collection name
    """
    return {
        "label": f"Add '{collection}' host collection to '{keyname}' activation key",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "hammer activation-key add-host-collection --name='" + keyname + "'"
                    + " --organization='" + orgname + "' --host-collection='" + collection + "'",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot add host collection to the activation key.",
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


def remove_usergroup(keyname):
    """
    Remove a user group
    'keyname' is a str with the key name
    """
    return {
        "label": f"Remove '{keyname}' user group",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer user-group list --search '" + keyname + "'"
                    + " --fields Name | grep '" + keyname + "') ]];"
                    + " then hammer user-group delete"
                    + " --name '" + keyname + "'"
                    + " ; exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot remove the user group.",
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


def update_capsule_org_loc(capsule, orgname, location):
    """
    Create the activation key for the given organization
    'capsule' is a str with the capsule name
    'orgname' is a str with the organization
    'location' is a str with the location name
    """
    return {
        "label": f"Update '{capsule}' to '{orgname}' organization and '{location}' location",
        "task": tasks.run_command,
        "hosts": ["satellite"],
        "username": "root",
        "password": "redhat",
        "command": "if [[ $(hammer --no-headers capsule list --search "
                    + capsule + " --fields Name) ]];"
                    + " then if [[ $(hammer capsule info --name "
                    + capsule + " --fields Locations | grep Boston) ]];"
                    + " then exit 0;"
                    + " else hammer capsule update"
                    + " --name " + capsule
                    + " --organizations='" + orgname + "'"
                    + " --locations='" + location + "';"
                    + " fi; else exit 0; fi",
        "returns": 0,
        "prints": '',
        "options": [],
        "fatal": False,
        "student_msg": "Cannot update capsule.",
        "sshkey": '',
        "shell": True
    }
