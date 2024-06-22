#!/bin/bash
# Syntax:
# $ sh remove_cvs.sh ORGANIZATION

ORGNAME=${1}

if [ -z $ORGNAME ]
then
    echo "Missing organization"
else
    for HOST in $(hammer --no-headers host list --organization "$ORGNAME" --fields Name,'Content view' | grep -v "Default Organization View" | awk '{ print $1 }')
    do
        echo "Move" $HOST "host to Default Organization View CV"
        hammer host update \
        --lifecycle-environment 'Library' \
        --content-view 'Default Organization View' \
        --organization "$ORGNAME" \
        --name $HOST
    done

    for COMPOSITE in $(hammer --no-headers content-view list --organization "$ORGNAME" --composite yes --fields Name)
    do
        for AKEY in $(hammer --no-headers  activation-key list --organization "$ORGNAME" --content-view "$CONTENTVIEW" --fields Name)
        do
            echo "Remove" $AKEY "Activation Key"
            hammer activation-key delete --name "$AKEY" --organization "$ORGNAME"
        done

        for FILTER in $(hammer --no-headers content-view filter list --content-view "$COMPOSITE" --organization "$ORGNAME" --fields Name)
        do
            echo "Remove" $FILTER "filter in" $COMPOSITE "CV"
            hammer content-view filter delete \
            --organization "$ORGNAME" \
            --content-view "$COMPOSITE" \
            --name "$FILTER"
        done

        for CVLC in $(hammer content-view info --name "$COMPOSITE" --organization "$ORGNAME" --fields 'Lifecycle environments/id' | grep Id | awk '{ print $3 }' | sort -nr)
        do
            echo "Remove LC id" $CVLC "from" $COMPOSITE "Composite CV"
            hammer content-view remove-from-environment \
            --name "$COMPOSITE" \
            --organization "$ORGNAME" \
            --lifecycle-environment-id $CVLC
        done

        echo "Remove" $COMPOSITE "Composite CV"
        hammer content-view delete \
        --name "$COMPOSITE" \
        --organization "$ORGNAME"
    done

    for CONTENTVIEW in $(hammer --no-headers content-view list --organization "$ORGNAME" --fields 'Content view id',Name | sort -nr | awk -F "|" '{ print $2 }' | sed 's/^[[:space:]]*//' | grep -v "Default Organization View")
    do
        for AKEY in $(hammer --no-headers  activation-key list --organization "$ORGNAME" --content-view "$CONTENTVIEW" --fields Name)
        do
            echo "Remove" $AKEY "Activation Key"
            hammer activation-key delete --name "$AKEY" --organization "$ORGNAME"
        done

        for FILTER in $(hammer --no-headers content-view filter list --content-view "$CONTENTVIEW" --organization "$ORGNAME" --fields Name)
        do
            echo "Remove" $FILTER "filter in" $CONTENTVIEW "CV"
            hammer content-view filter delete \
            --organization "$ORGNAME" \
            --content-view "$CONTENTVIEW" \
            --name "$FILTER"
        done

        for CVLC in $(hammer content-view info --name "$CONTENTVIEW" --organization "$ORGNAME" --fields 'Lifecycle environments/id' | grep Id | awk '{ print $3 }' | sort -nr)
        do
            echo "Remove LC id" $CVLC "from" $CONTENTVIEW "CV"
            hammer content-view remove-from-environment \
            --name "$CONTENTVIEW" \
            --organization "$ORGNAME" \
            --lifecycle-environment-id $CVLC
        done
        
        echo "Remove" $CONTENTVIEW "CV"
        hammer content-view delete \
        --name "$CONTENTVIEW" \
        --organization "$ORGNAME"
    done
fi