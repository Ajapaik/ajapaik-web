#!/bin/bash

cd /etc/nginx/sites-enabled && ln -s /etc/nginx/sites-available/ajapaik_ee_$1 /etc/nginx/sites-enabled/test_ajapaik_ee && sudo service nginx reload