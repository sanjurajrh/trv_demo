#!/bin/bash
#
orgname="Operations"
ops_cv="OperationsServerBase"
ops_cv_desc="Base Packages"

fqdn_servera="servera.lab.example.com"

liblc="Library"
devlc="Development"
devdesc="Development"
qalc="QA"
qadesc="Quality Assurance"
prodlc="Production"
proddesc="Production"

credname="Example Software"

prod_name="Custom Software"
repo_name="Admin Tools"

cv_counter=$(hammer --no-headers content-view list --organization $orgname | grep $ops_cv | wc -l)
if [ $cv_counter -gt 0 ];
then
	hammer --no-headers content-view version list --content-view $ops_cv --organization $orgname | grep "$repo_name" > /dev/null 2> /dev/null
	if [ $? -eq 0 ];
	then
		cv_ver=$(hammer --no-headers content-view version list --content-view $ops_cv --organization $orgname | grep "$repo_name" | awk '{ print $1 }' )
		hammer host delete --name $fqdn_servera --organization $orgname > /dev/null 2> /dev/null
		hammer --no-headers content-view remove-from-environment --lifecycle-environment-id 5 --name $ops_cv --organization $orgname > /dev/null 2> /dev/null 
		hammer --no-headers content-view remove-from-environment --lifecycle-environment-id 3 --name $ops_cv --organization $orgname > /dev/null 2> /dev/null 
		hammer content-view version delete --content-view $ops_cv --id $cv_ver --organization $orgname > /dev/null 2> /dev/null
		hammer repository delete --organization $orgname --product="$prod_name" --name="$repo_name" > /dev/null 2> /dev/null
		for i in $(hammer --no-headers content-view version list --content-view $ops_cv --organization $orgname --fields='id')
		do
			hammer content-view version delete --content-view $ops_cv --id $i --organization $orgname > /dev/null 2> /dev/null
		done
	fi
fi
