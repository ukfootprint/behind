#!/bin/bash

# From https://www.github.com/dhicks6345789/remote-gateway

# Stop Nginx so Certbot can go ahead and run.
# Don't think this is necessary - SH
#systemctl stop nginx

# This script should be run at least every two months (i.e. <90 days) to auto-renew the Let's Encrypt SSL certificate.
# Running more often (every day / week) doesn't do any harm, though.
certbot renew

# After renewing, backup the new SSL certificate.
#tar cf /root/...

# No need to restart - reload instead
#systemctl start nginx
systemctl reload nginx
