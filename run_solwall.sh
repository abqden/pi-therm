#!/bin/bash
echo "greetings from run_solwall.sh" &> /dev/null
ps -eo "%P %a" | grep solwall | grep python &> /dev/null

if [ $? -eq 0 ]
then
	echo "returned 0, so solwall is already running" &> /dev/null
else
	echo "starting solwall.py" &> /dev/null
	/usr/bin/python /home/pi/solwall.py&
fi

exit 0
# don't forget to chmod +x to CRONTAB can run script

