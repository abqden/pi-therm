#!/usr/bin/python

"""

The Python sys module provides access to any command-line arguments via the sys.argv.
This serves two purpose: sys.argv is the list of command-line arguments.
len(sys.argv) is the number of command-line arguments. Here sys.argv[0] is the program ie. script name.

"""

# -----------------------
# Imports
# -----------------------

import os
import socket
import subprocess
import signal # to catch exceptions
import sys
import time
import logging
from time import sleep

logging.basicConfig(format='slot_wall_mode.py: \
  %(levelname)s %(asctime)s  %(message)s', \
  #filename = 'toss.txt',
  level=logging.INFO)


import cgi
import cgitb
cgitb.enable()



# -----------------------
# Define some variables
# -----------------------

GET_IP_CMD = "hostname --all-ip-addresses"
alarm_channel = 1623
gate = "192.168.0.87"
ham = "192.168.0.81"
port = 1611
buffsize = 1024
End="__END__" # end of message marker for recv_end subroutine

solwall_auto = "hello"

isolwall_auto = """
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
"""


# -----------------------
# Define some functions
# -----------------------


def run_cmd(cmd):
    return subprocess.check_output(cmd, shell=True).decode('utf-8')

def get_my_ip():
    return run_cmd(GET_IP_CMD)[:-1]

def wait_for_ip():
    ip = ""
    while len(ip) <= 0:
        time.sleep(1)
        ip = get_my_ip()

def recv_end(sock):
    total_data=[];data=''
    while True:
        data=sock.recv(buffsize)
        if (len(data)<1):
            break
        if End in data:
            total_data.append(data[:data.find(End)])
            break
        total_data.append(data)
        if len(total_data)>1:
            #check if end_of_data was split
            last_pair=total_data[-2]+total_data[-1]
            if End in last_pair:
                total_data[-2]=last_pair[:last_pair.find(End)]
                total_data.pop()
                break
    return ''.join(total_data)



def set_manual():
    fd_auto = open('solwall.mode', 'w')
    fd_auto.write("manual")
    fd_auto.close()
    
def set_auto():
    fd_auto = open('solwall.mode', 'w')
    fd_auto.write("auto")
    fd_auto.close()
    



##############
# Begin MAIN #
##############

form=cgi.FieldStorage()
logging.debug ( "form is {:}".format(form))

if "Option" not in form:
    print "No buttons were selected."
else:
    value = form.getlist("Option")
    Option = ",".join(value)
    logging.debug ( "Option list is {:}".format(Option))
    
    if Option == "manual":
        set_manual()
        print "Now on manual"
    
    if Option == "auto":
        set_auto()
        print "Now on auto"

#webbrowser.open('http://192.168.0.82/manual.html')

#print cgi.escape("Use back button to return to previous screen.")