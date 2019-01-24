#!/bin/bash

/etc/init.d/nginx stop && certbot renew &&/etc/init.d/nginx start
