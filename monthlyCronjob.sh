#!/bin/bash

# Stop Nginx so Certbot can go ahead and run.
systemctl stop nginx

# This script should be run at least every two months (i.e. <90 days) to auto-renew the Let's Encrypt SSL certificate.
# Running more often (every day / week) doesn't do any harm, though.
certbot renew

# After renewing, backup the new SSL certificate.
#tar cf /root/...

systemctl start nginx
