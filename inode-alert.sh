#!/bin/sh
df -i | grep -vE '^Filesystem|tmpfs|cdrom' | awk '{ print $3 "/" $2  }' | while read output;
do
  echo $output
done

