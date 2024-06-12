#!/bin/bash
cat <<'EOF' >/var/www/cgi-bin/health
#!/bin/bash
if [ -f /etc/maintenance ]
then
echo -e 'Status: 503 Service Unavailable\n\n'
else
echo -e 'Content-type: text/html\n'
echo '<html><head><title>Web Application Status</title></head><body>OK</body></html>'
fi
EOF
chmod 755 /var/www/cgi-bin/health

curl --output /root/mount.sh http://utility.lab.example.com:8080/mount.sh
chmod 700 /root/mount.sh
