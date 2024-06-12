#!/bin/bash

IMAGE=registry.ocp4.example.com:8443/ubi8/ubi
OCP_URL=https://api.ocp4.example.com:6443
OCP_USER=admin
OCP_PASS=redhatocp
NAMESPACE=${1:-network-review}
POD=testweb
WEB_URL=http://web.network-review:8080
MESSAGE=""

echo "Testing web application from ${NAMESPACE} (be patient)..."

(
  oc login -u ${OCP_USER} -p ${OCP_PASS} ${OCP_URL}
  oc delete pod ${POD} -n "${NAMESPACE}"
) &> /dev/null

oc run ${POD} -i --rm -n "${NAMESPACE}" --image=${IMAGE} -- \
  bash -c "sleep 1 ; curl --max-time 10 -fsSL ${WEB_URL}" 2>/dev/null | \
grep -qiE "hello.*world"

if [ $? -eq 0 ]
then
  MESSAGE="Connection successful"
else
  MESSAGE="Cannot connect to ${WEB_URL}"
fi

(
  oc delete pod ${POD} -n "${NAMESPACE}"
) &> /dev/null
  
printf "\t%s\n" "${MESSAGE}"
