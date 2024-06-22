#!/bin/bash
vcounter=0;
vbasel='Red_Hat_Enterprise_Linux_9_for_x86_64_-_BaseOS_RPMs_9';
vappsl='Red_Hat_Enterprise_Linux_9_for_x86_64_-_AppStream_RPMs_9';
vclientl='Red_Hat_Satellite_Client_6_for_RHEL_9_x86_64_RPMs';
vcview="FinanceServerBase";
vorgname="Finance";
vlcdev="Build";
vlcdevdes="Build Packages";

version_total=$(hammer --no-headers content-view version list --content-view $vcview --organization $vorgname --fields Version | wc -l);

if [ $version_total -eq 1 ]; then
    if [[ $(hammer content-view version info --content-view $vcview --organization  $vorgname --version $(hammer --no-headers content-view version list --content-view $vcview --organization $vorgname --fields Version) --fields='Repositories/label' | grep $vbasel) ]]; then
        if [[ $(hammer content-view version info --content-view $vcview --organization  $vorgname --version $(hammer --no-headers content-view version list --content-view $vcview --organization $vorgname --fields Version) --fields='Repositories/label' | grep Red_Hat | grep -v $vbasel) ]]; then
            vcounter=2;
        else
            vcounter=1;
        fi;
    else
        vcounter=2;
    fi;
else 
    vversionarray=( $(hammer --no-headers content-view version list --content-view $vcview --organization $vorgname --fields Version | head -n2) );
    if [[ $(hammer content-view version info --content-view $vcview --organization  $vorgname --fields Repositories/Label --version ${vversionarray[0]} | egrep $vbasel\|$vappsl\|$vclientl | wc -l) -eq 3 ]]; then
        if [[ $(hammer content-view version info --content-view $vcview --organization  $vorgname --fields Repositories/Label --version ${vversionarray[1]} | grep Red_Hat | wc -l) -eq 1 ]]; then
            if [[ $(hammer content-view version info --content-view $vcview --organization  $vorgname --fields Repositories/Label --version ${vversionarray[1]} | grep $vbasel | wc -l) -eq 1 ]]; then
                vcounter=0;
            else
                vcounter=2;
            fi;
        else
            vcounter=2;
        fi;
    else
        vcounter=2;
    fi;
fi;

if [[ $vcounter -eq 2 ]]; then
    for vrepo in $(hammer content-view info --name $vcview --organization $vorgname --fields='Yum repositories/label' | grep Red_Hat | grep -v BaseOS | awk '{print $3}'); do
        echo 'Remove repo: ' $vrepo;
        hammer content-view remove-repository --name $vcview --organization $vorgname --repository-id $(hammer --no-headers repository list --organization $vorgname --label $vrepo --fields Id);
    done;
    echo 'Add repo: ' $vbasel ' to cv: ' $vcview;
    hammer content-view add-repository --name $vcview --organization $vorgname --repository-id $(hammer --no-headers repository list --organization $vorgname --fields Id --label $vbasel);
    echo 'Publish cv: ' $vcview;
    hammer content-view publish --name $vcview --description "$vlcdevdes" --organization $vorgname;
    echo 'Promote cv: ' $vcview ' to lc: ' $vlcdev;
    hammer content-view version promote --content-view $vcview --to-lifecycle-environment $vlcdev --description "$vlcdevdes" --organization $vorgname --id $(hammer --no-headers  content-view version list --organization  $vorgname --version $(hammer --no-headers content-view version list --content-view $vcview --organization $vorgname --fields Version | sort -r | head -n1) --fields Id);
fi;
if [[ $vcounter -eq 1 ]] || [[ $vcounter -eq 2 ]]; then
    echo 'Add repo: ' $vappsl ' to cv: ' $vcview;
    hammer content-view add-repository --name $vcview --organization $vorgname --repository-id $(hammer --no-headers repository list --organization $vorgname --fields Id --label $vappsl);
    echo 'Add repo: ' $vclientl ' to cv: ' $vcview;
    hammer content-view add-repository --name $vcview --organization $vorgname --repository-id $(hammer --no-headers repository list --organization $vorgname --fields Id --label $vclientl);
    echo 'Publish cv: ' $vcview;
    hammer content-view publish --name $vcview --description "$vlcdevdes" --organization $vorgname;
    echo 'Promote cv: ' $vcview ' to lc: ' $vlcdev;
    hammer content-view version promote --content-view $vcview --to-lifecycle-environment $vlcdev --description "$vlcdevdes" --organization $vorgname --id $(hammer --no-headers  content-view version list --organization  $vorgname --version $(hammer --no-headers content-view version list --content-view $vcview --organization $vorgname --fields Version | sort -r | head -n1) --fields Id);
fi;
