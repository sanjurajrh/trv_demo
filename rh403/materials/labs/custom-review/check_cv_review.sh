#!/bin/bash
#
orgname="Finance"
fin_cv="FinanceServerBase"

fqdn_serverb="serverb.lab.example.com"

prod_name="Custom Software"
repo_name="Admin Tools"
cred_name="Example Software"

cv_counter=$(hammer --no-headers content-view list --organization $orgname | grep "$fin_cv" | wc -l)
if [ $cv_counter -gt 0 ];
then
	cv_ver=$(hammer --no-headers content-view version list --content-view $fin_cv --organization $orgname --fields='id' | head -1)
	hammer --no-headers content-view version show --id $cv_ver --content-view $fin_cv --organization $orgname --fields='Repositories' | grep "$repo_name" > /dev/null 2> /dev/null
	if [ $? -eq 0 ];
	then
		hammer host delete --name $fqdn_serverb --organization $orgname > /dev/null 2> /dev/null
		hammer --no-headers content-view remove-from-environment --lifecycle-environment-id 5 --name $fin_cv --organization $orgname > /dev/null 2> /dev/null 
		hammer --no-headers content-view remove-from-environment --lifecycle-environment-id 4 --name $fin_cv --organization $orgname > /dev/null 2> /dev/null 
		hammer content-view version delete --content-view $fin_cv --id $cv_ver --organization $orgname > /dev/null 2> /dev/null
		hammer repository delete --organization $orgname --product="$prod_name" --name="$repo_name" > /dev/null 2> /dev/null
		hammer product delete --name="$prod_name" --organization $orgname > /dev/null 2> /dev/null
		hammer content-credentials delete --organization $orgname --name="$cred_name" > /dev/null 2> /dev/null
		for i in $(hammer --no-headers content-view version list --content-view $fin_cv --organization $orgname --fields='id')
		do
			hammer content-view version delete --content-view $fin_cv --id $i --organization $orgname > /dev/null 2> /dev/null
		done
	fi
fi
