#!/bin/bash
MESSAGE=""
TARGET="telnet://database:3306"

echo -n 'Content-type: text/html; charset=UTF-8'
echo -en '\r\n\r\n'

curl --max-time 5 --output /dev/null "${TARGET}" &> /dev/null <<< "test"
RET=$?
if [ $RET -eq 0 -o $RET -eq 28 -o $RET -eq 56 ]
then
    MESSAGE='<p style="color:green;">PASS</p>'
else
    MESSAGE='<p style="color:red;">FAIL</p>'
fi

echo '<html><head><title>Database Test</title></head><body>'
echo "${MESSAGE}"
echo '</body></html>'
