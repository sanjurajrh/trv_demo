#!/bin/bash

IMAGE=registry.ocp4.example.com:8443/rhel8/mariadb-103
OCP_URL=https://api.ocp4.example.com:6443
OCP_USER=admin
OCP_PASS=redhatocp
NAMESPACE=${1:-network-review}
POD=testdb
DB_HOST=database.network-review
DB_USER=devuser
DB_PASS=developer
DB_NAME=sakila
DB_QUERY='SELECT first_name FROM actor WHERE actor_id=1'
MESSAGE=""

echo "Testing database connection from ${NAMESPACE} (be patient)..."

(
  oc login -u ${OCP_USER} -p ${OCP_PASS} ${OCP_URL}
  oc delete pod ${POD} -n "${NAMESPACE}"
) &> /dev/null

oc run ${POD} -i --rm -n "${NAMESPACE}" --image=${IMAGE} -- \
  bash -c "sleep 2 ; mysql --batch --connect-timeout=10 \
    --user=${DB_USER} --password=${DB_PASS} --host=${DB_HOST} \
    --execute=\"${DB_QUERY}\" ${DB_NAME}" 2>/dev/null | \
grep -q first_name

if [ $? -eq 0 ]
then
  MESSAGE="Connection successful"
else
  MESSAGE="Cannot connect"
fi

(
  oc delete pod ${POD} -n "${NAMESPACE}"
) &> /dev/null

printf "\t%s\n" "${MESSAGE}"
