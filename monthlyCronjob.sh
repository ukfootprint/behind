#!/bin/bash

# Run at least every two months (i.e. <90 days) to auto-renew the Let's Encrypt SSL certificate, valid for 90 days
# Running more often (every day / week) doesn't do any harm, though.
certbot renew

# reload nginx to load new certificate
systemctl reload nginx
