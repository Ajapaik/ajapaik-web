#!/bin/bash
# File lives in ajapaik.ee:/usr/bin/start_ajapaik.sh

if [ "$EUID" -ne 0 ]
then
	echo "This script must be run as root."
	exit 1
fi

function slack_message {
        message={\"text\":\"$1\"}
        curl -X POST -H 'Content-type: application/json' --data "$message" https://hooks.slack.com/services/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
}

if [ "$1" = "start" ]
then
	cd /home/ajapaik/
	echo "Starting docker"
	docker-compose up -d
	echo "Waiting for 30 seconds for Docker to start"
	sleep 30

        echo "Copying bktree.so"
        docker container cp /home/ajapaik/pg-spgist_hamming/bktree/bktree.so postgis:/usr/local/lib/postgresql/bktree.so
	echo "Starting supervisor"
	supervisorctl start ajapaik_ee

	echo "Testing that new.ajapaik.ee works"
	declare -i retryAttempts=1

	while :
	do
		if [ $retryAttempts -gt 5 ]
		then
			echo "Retried 5 times, giving up"
			slack_message "$(date) ajapaik.ee: Ajapaik services failed to start, response code on ajapaik.ee was $responseCode"
			exit 1
		fi

		responseCode=$(curl -o /dev/null -s -w "%{http_code}\n" https://ajapaik.ee)
		if [ $responseCode = "200" ]
			then
				echo "new.ajapaik.ee is up"
				break
			else
				echo "Response code is $responseCode , retrying in 15 seconds"
				echo $((retryAttempts++))
				sleep 5
		fi
	done

	echo "Starting IIIF"
	systemctl start iipsrv

	echo "Checking that IIIF is up"
	declare -i retryAttempts=1

	while :
	do
		if [ $retryAttempts -gt 5 ]
		then
			echo "Retried 5 times, giving up"
			slack_message "$(date) ajapaik.ee: Ajapaik services failed to start, response code on IIIF was $responseCode"
			exit 1
		fi

		responseCode=$(curl -o /dev/null -s -w "%{http_code}\n" https://ajapaik.ee/fcgi-bin/iipsrv.fcgi)
		if [ $responseCode  = "200" ]
		then
			echo "IIIF is up"
			break
		else
			echo "Response code is $responseCode , retrying in 15 seconds"
			echo $((retryAttempts))
			sleep 5
		fi
	done

	echo "Startup complete"

	slack_message "$(date) ajapaik.ee: Ajapaik services succesfully started"
	exit 0
fi

if [ "$1" = "stop" ]
then
	echo "Stopping iipserv"
	systemctl stop iipsrv

	echo "Stopping supervisor"
	supervisorctl stop ajapaik_ee

	cd /home/ajapaik/
	echo "Stopping docker"
	docker-compose down

	echo "Stop complete"
	exit 0
fi

echo "Script to start ajapaik services"
echo "syntax: start_ajapaik.sh <options>"
echo -e "\n"
echo "Valid options:"
echo "start: Start services"
echo "stop: Stop services"
