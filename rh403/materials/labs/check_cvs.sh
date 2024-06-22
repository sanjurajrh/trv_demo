#!/bin/bash
# Syntax:
# $ sh check_cvs.sh ORGANIZATION CONTENTVIEW

REPO_BASE='Red_Hat_Enterprise_Linux_9_for_x86_64_-_BaseOS_RPMs_9';
REPO_APPSTREAM='Red_Hat_Enterprise_Linux_9_for_x86_64_-_AppStream_RPMs_9';
REPO_CLIENT='Red_Hat_Satellite_Client_6_for_RHEL_9_x86_64_RPMs';

TO_DO=0;

ORGANIZATION=${1};
CONTENTVIEW=${2};

CreateCV(){
    echo "Create" $CONTENTVIEW "in" $ORGANIZATION
    hammer content-view create --name "$CONTENTVIEW" --label "$CONTENTVIEW" --organization "$ORGANIZATION"
}

VersionPromote(){
    echo "Promote Version" $2 "to LC" $1
    hammer content-view version promote --force --content-view $CONTENTVIEW --organization $ORGANIZATION --version $2 --to-lifecycle-environment $1
}

AddRepo(){
    REPO_ID=$(hammer --no-headers repository list --organization $ORGANIZATION --label $1 --fields Id)
    echo "Add repo label" $1 "with ID" $REPO_ID "to" $CONTENTVIEW "CV"
    hammer content-view add-repository --name $CONTENTVIEW --organization $ORGANIZATION --repository-id $REPO_ID
}

PublishCV(){
    echo "Publish" $CONTENTVIEW "CV"
    hammer content-view publish --name $CONTENTVIEW --organization $ORGANIZATION
}

RemoveRepo(){
    REPO_ID=$(hammer --no-headers repository list --organization $ORGANIZATION --label $1 --fields Id)
    echo "Remove repo label" $1 "with ID" $REPO_ID "from" $CONTENTVIEW "CV"
    hammer content-view remove-repository --name $CONTENTVIEW --organization $ORGANIZATION --repository-id $REPO_ID
}


if [ -z $ORGANIZATION ] || [ -z $CONTENTVIEW ]
then
    echo "Missing input"
    echo "sh check_cvs.sh ORGANIZATION CONTENTVIEW"
else
    TOTAL_VERSIONS=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | wc -l);
    echo "Total versions:" $TOTAL_VERSIONS
    if [ $TOTAL_VERSIONS -eq 0 ]
    then
        CreateCV
        AddRepo $REPO_BASE
        PublishCV
        LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
        VersionPromote Development $LATEST_VERSION
        VersionPromote QA $LATEST_VERSION
        AddRepo $REPO_APPSTREAM
        AddRepo $REPO_CLIENT
        PublishCV
        LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
        VersionPromote Development $LATEST_VERSION
    elif [ $TOTAL_VERSIONS -eq 1 ]
    then
        LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version)
        if [[ $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Repositories/label' | grep Red_Hat | wc -l) -eq 1 ]]
        then
            if [[ $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Repositories/label' | grep $REPO_BASE) ]]
            then
                if [[ $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Lifecycle Environments/Name' | egrep "Library|Development|QA" | wc -l) -eq 3 ]]
                then
                    AddRepo $REPO_BASE
                    AddRepo $REPO_APPSTREAM
                    AddRepo $REPO_CLIENT
                    PublishCV
                    LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
                    VersionPromote Development $LATEST_VERSION
                else
                    VersionPromote Development $LATEST_VERSION
                    VersionPromote QA $LATEST_VERSION
                    AddRepo $REPO_BASE
                    AddRepo $REPO_APPSTREAM
                    AddRepo $REPO_CLIENT
                    PublishCV
                    LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
                    VersionPromote Development $LATEST_VERSION
                fi
            else
                LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
                for WRONG_REPO in $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Repositories/label' | grep Red_Hat | awk '{ print $3 }' | grep -v $REPO_BASE)
                do
                    RemoveRepo $WRONG_REPO
                done
                AddRepo $REPO_BASE
                PublishCV
                LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
                VersionPromote Development $LATEST_VERSION
                VersionPromote QA $LATEST_VERSION
                AddRepo $REPO_APPSTREAM
                AddRepo $REPO_CLIENT
                PublishCV
                LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
                VersionPromote Development $LATEST_VERSION
            fi
        else
            for WRONG_REPO in $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Repositories/label' | grep Red_Hat | awk '{ print $3 }' | grep -v $REPO_BASE)
            do
                RemoveRepo $WRONG_REPO
            done
            AddRepo $REPO_BASE
            PublishCV
            LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
            VersionPromote Development $LATEST_VERSION
            VersionPromote QA $LATEST_VERSION
            AddRepo $REPO_APPSTREAM
            AddRepo $REPO_CLIENT
            PublishCV
            LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
            VersionPromote Development $LATEST_VERSION
        fi
    else
        LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
        PENULTIMATE_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n2 | tail -n1)
        if [[ $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Repositories/label' | egrep "$REPO_BASE|$REPO_APPSTREAM|$REPO_CLIENT" | wc -l) -eq 3 ]]
        then
            if [[ $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Lifecycle Environments/Name' | egrep "Library|Development|QA" | wc -l) -eq 2 ]] && [[ $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Lifecycle Environments/Name' | grep "QA" | wc -l) -ne 1 ]]
            then
                echo "Lastest version is good"
                if [[ $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $PENULTIMATE_VERSION --fields='Repositories/label' | egrep "$REPO_BASE|$REPO_APPSTREAM|$REPO_CLIENT" | wc -l) -eq 1 ]] && [[ $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $PENULTIMATE_VERSION --fields='Repositories/label' | egrep "$REPO_BASE") ]]
                then
                    echo "Penultimate version is good"
                else
                    for WRONG_REPO in $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Repositories/label' | grep Red_Hat | awk '{ print $3 }' | grep -v $REPO_BASE)
                    do
                        RemoveRepo $WRONG_REPO
                    done
                    AddRepo $REPO_BASE
                    PublishCV
                    LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
                    VersionPromote Development $LATEST_VERSION
                    VersionPromote QA $LATEST_VERSION
                    AddRepo $REPO_APPSTREAM
                    AddRepo $REPO_CLIENT
                    PublishCV
                    LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
                    VersionPromote Development $LATEST_VERSION
                fi
            else
                VersionPromote Library $LATEST_VERSION
                VersionPromote Development $LATEST_VERSION
                VersionPromote QA $PENULTIMATE_VERSION
            fi
        else
            for WRONG_REPO in $(hammer content-view version info --content-view $CONTENTVIEW --organization  $ORGANIZATION --version $LATEST_VERSION --fields='Repositories/label' | grep Red_Hat | awk '{ print $3 }' | grep -v $REPO_BASE)
            do
                RemoveRepo $WRONG_REPO
            done
            AddRepo $REPO_BASE
            PublishCV
            LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
            VersionPromote Development $LATEST_VERSION
            VersionPromote QA $LATEST_VERSION
            AddRepo $REPO_APPSTREAM
            AddRepo $REPO_CLIENT
            PublishCV
            LATEST_VERSION=$(hammer --no-headers content-view version list --content-view $CONTENTVIEW --organization $ORGANIZATION --fields Version | head -n1)
            VersionPromote Development $LATEST_VERSION
        fi
    fi
fi