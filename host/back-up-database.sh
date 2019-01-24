#!/bin/bash

sudo su - postgres && pg_dump rephoto_production -s -f rephoto_$(date +%F).schema.dump && \
    pg_dump rephoto_production -Fc -f rephoto_$(date +%F).sql

# TODO: Upload to Google Drive
