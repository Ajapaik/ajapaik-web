#!/bin/bash
export HOME=/home/fotodugnad
cd $HOME
source venv/bin/activate
cd $HOME/ajapaik-web/
uwsgi --socket /home/fotodugnad/ajapaik-web/fotodugnad.sock --module project.ajapaik.wsgihandler --chmod-socket=777 --env=LANG="en_US.utf8" --processes 8 --master --harakiri 180 --max-requests 500

exit $?
