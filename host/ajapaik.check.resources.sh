#!/bin/bash
# File lives in ajapaik.ee:/usr/bin/ajapaik.check.resources.sh


function slack_message {
	echo $1
        message={\"text\":\"$1\"}
        curl -X POST -H 'Content-type: application/json' --data "$message" https://hooks.slack.com/services/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
}

## check if system load is over 8.0 during last 15 minutes
systemLoad=$(uptime | awk '{print $NF}')
systemLoadCompared=$(echo 'l='$systemLoad';if(l>8.0) print "true" else print "false" ' | bc -l)

if [ "$systemLoadCompared" == "true" ]
then
	slack_message "$(date) ajapaik.ee: Warning: System load is over 8.0 during the past 15 minutes, load is: $systemLoad"
fi

## check memory usage
memoryUsage=$(free -m | grep Mem | awk '{print ($3/$2)*100}')
swapUsage=$(free -m | grep Swap | awk '{print ($3/$2)*100}')

memoryUsageCompared=$(echo 'u='$memoryUsage';if(u>80.0) print "true" else print "false" ' | bc -l)
swapUsageCompared=$(echo 'u='$swapUsage';if(u>80.0) print "true" else print "false" ' | bc -l)

if [ "$memoryUsageCompared" == "true" ]
then
	slack_message "$(date) ajapaik.ee: Warning: Memory usage is $memoryUsage %"
	if [ "$swapUsageCompared" == "true" ]
	then
		slack_message "$(date) ajapaik.ee: Warning: Swap usage is also high, current swap usage is: $swapUsage %"
	fi
fi

## check disk space
for blockdevice in '/sda2' '/sdb1' '/sdc1'; do
	declare -i ajapaik_disk_usage=0
	ajapaik_disk_usage=$(df -hl | grep $blockdevice | awk '{print $5}' | sed 's/%//')

	if [ $ajapaik_disk_usage -gt 80 ]
	then
		slack_message "$(date) ajapaik.ee: Warning: ajapaik disk /dev$blockdevice usage is $ajapaik_disk_usage"
	fi
done
