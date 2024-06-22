#!/bin/bash
#
orgname="Finance"
fin_cv="FinanceServerBase"
def_cv="Default Organization View"
lcname="Library"

prod_name="Red Hat Enterprise Linux for x86_64"
repo_1="Red Hat Enterprise Linux 9 for x86_64 - BaseOS Kickstart 9.0"
repo_2="Red Hat Enterprise Linux 9 for x86_64 - AppStream Kickstart 9.0"

find_cv=$(hammer --no-headers content-view version list --organization $orgname | grep "$fin_cv" | wc -l)
if [ $find_cv -gt 0 ];
then
	cv_id=$(hammer --no-headers content-view version list --organization $orgname | grep "$fin_cv" | head -1 | awk '{ print $1}')
	find_ks=$(hammer --no-headers content-view version info --content-view $fin_cv --id $cv_id --organization $orgname --fields Repositories | grep -i "kickstart" | wc -l)
	if [ $find_ks -gt 0 ];
	then
		cv_host=$(hammer --no-headers host list --organization $orgname --fields Name,'Content view' | grep "$fin_cv" | wc -l)
		if [ $cv_host -gt 0 ];
		then
			host=$(hammer --no-headers host list --organization $orgname --fields Name,'Content view' | grep "$fin_cv" | awk '{ print $1 }')
			hammer host update --lifecycle-environment "$lcname" --content-view "$def_cv" --organization $orgname --name $host > /dev/null 2> /dev/null
			hammer --no-headers content-view remove-from-environment --lifecycle-environment-id 5 --name $fin_cv --organization $orgname > /dev/null 2> /dev/null 
			hammer --no-headers content-view remove-from-environment --lifecycle-environment-id 4 --name $fin_cv --organization $orgname > /dev/null 2> /dev/null 
			hammer content-view version delete --content-view $fin_cv --id $cv_id --organization $orgname > /dev/null 2> /dev/null
			hammer repository delete --organization $orgname --product="$prod_name" --name="$repo_1" > /dev/null 2> /dev/null
			hammer repository delete --organization $orgname --product="$prod_name" --name="$repo_2" > /dev/null 2> /dev/null
			last_cv_id=$(hammer --no-headers content-view version list --content-view $fin_cv --organization $orgname | head -1 | awk '{ print $1 }')
			cv_ver_le=$(hammer --no-headers content-view version info --id $last_cv_id --content-view $fin_cv --organization $orgname --fields 'Lifecycle environments/name' | grep "$lcname" | wc -l)
			if [ $cv_ver_le -eq 0 ];
				then
				hammer content-view version promote --content-view $fin_cv --id $last_cv_id --to-lifecycle-environment $lcname --description $lcname --force --organization $orgname > /dev/null 2> /dev/null
				hammer host update --lifecycle-environment "$lcname" --content-view "$fin_cv" --organization $orgname --name $host > /dev/null 2> /dev/null
			fi
		else
			hammer --no-headers content-view remove-from-environment --lifecycle-environment-id 5 --name $fin_cv --organization $orgname > /dev/null 2> /dev/null 
			hammer --no-headers content-view remove-from-environment --lifecycle-environment-id 4 --name $fin_cv --organization $orgname > /dev/null 2> /dev/null 
			hammer content-view version delete --content-view $fin_cv --id $cv_id --organization $orgname > /dev/null 2> /dev/null
			hammer repository delete --organization $orgname --product="$prod_name" --name="$repo_1" > /dev/null 2> /dev/null
			hammer repository delete --organization $orgname --product="$prod_name" --name="$repo_2" > /dev/null 2> /dev/null
			last_cv_id=$(hammer --no-headers content-view version list --content-view $fin_cv --organization $orgname | head -1 | awk '{ print $1 }')
			cv_ver_le=$(hammer --no-headers content-view version info --id $last_cv_id --content-view $fin_cv --organization $orgname --fields 'Lifecycle environments/name' | grep "$lcname" | wc -l)
			if [ $cv_ver_le -eq 0 ];
				then
					hammer content-view version promote --content-view $fin_cv --id $last_cv_id --to-lifecycle-environment $lcname --description $lcname --force --organization $orgname > /dev/null 2> /dev/null
			fi
		fi
	fi
fi
