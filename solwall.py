#!/usr/bin/python
# solwall.py

#================================================================
# Imports
#----------------------------------------------------------------
import os, sys
import glob
import time
import datetime
import logging

# -----------------------
# Define some variables
# -----------------------

#logging.basicConfig(format='solwall %(levelname)s: %(asctime)s  %(message)s', level=logging.INFO)
# if you set level=logging.INFO it will supress all the logging.debug messages
logging.basicConfig(format='solwall %(levelname)s: %(asctime)s  %(message)s', filename='/run/shm/toss.txt', level=logging.DEBUG)

global operating_mode
operating_mode='auto'

global quarterly
quarterly='no'

global mudroom, left_actual, mid_actual, right_actual, left_temp, mid_temp, right_temp,  \
Lower_left_state, Lower_mid_state, Lower_right_state

mudroom = left_actual = mid_actual = right_actual = left_temp = mid_temp = right_temp = \
Lower_left_state = Lower_mid_state = Lower_right_state = 0

global left_slot_state
left_slot_state="Open"
global mid_slot_state
mid_slot_state="Open"
global right_slot_state
right_slot_state="Open"

global upper_left_open
global upper_left_close
global lower_left_open
global lower_left_close

global upper_mid_open
global upper_mid_close
global lower_mid_open
global lower_mid_close

global upper_right_open
global upper_right_close
global lower_right_open
global lower_right_close

upper_left_servo  = "1"
lower_left_servo  = "4"
upper_mid_servo   = "6"
lower_mid_servo   = "3"
upper_right_servo = "2"
lower_right_servo = "5"

upper_left_open  = 'echo ' + upper_left_servo + '=90% > /dev/servoblaster'
upper_left_close = 'echo ' + upper_left_servo + '=5% > /dev/servoblaster'
lower_left_open  = 'echo ' + lower_left_servo + '=3% > /dev/servoblaster'
lower_left_close = 'echo ' + lower_left_servo + '=40% > /dev/servoblaster'

upper_mid_open  = 'echo ' + upper_mid_servo + '=70% > /dev/servoblaster'
upper_mid_close = 'echo ' + upper_mid_servo + '=1% > /dev/servoblaster'
lower_mid_open  = 'echo ' + lower_mid_servo + '=95% > /dev/servoblaster'
lower_mid_close = 'echo ' + lower_mid_servo + '=18% > /dev/servoblaster'

upper_right_open  = 'echo ' + upper_right_servo + '=80% > /dev/servoblaster'
upper_right_close = 'echo ' + upper_right_servo + '=3% > /dev/servoblaster'
lower_right_open  = 'echo ' + lower_right_servo + '=8% > /dev/servoblaster'
lower_right_close = 'echo ' + lower_right_servo + '=77% > /dev/servoblaster'

week   = ['Mon', 
          'Tue', 
          'Wed', 
          'Thu',  
          'Fri',
          'Sat',
          'Sun']


base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# -----------------------
# Define some functions
# -----------------------


def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp():
	lines = read_temp_raw()
# the following "while" re-reads lines [0] until the library reports YES got a good CRC
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
#If YES above, the second line has a good temperature reading
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
		temp_f = temp_c * 9.0 / 5.0 + 32.0
		return temp_c, temp_f
#the following def goes into the system and counts the number of master/slave 1 wire devices
def read_nr_devices():
	dev_count = open ("/sys/bus/w1/devices/w1_bus_master1/w1_master_slave_count", 'r')
	device_count = dev_count.read()
	dev_count.close()
	num_devices = int ( device_count)
	return (num_devices)

def fetch_temperatures():
    #os.system('modprobe w1-gpio gpiopin=25')
    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')
    time.sleep(1)

    nr_devices = read_nr_devices()

    #os.system ('PiBits/ServoBlaster/user/./servod') # servod is run by crontab now
    #activate servoblaster software

    device_folder = glob.glob(base_dir + '28*') [0] #middle
    device_file = device_folder + '/w1_slave'
    r=(read_temp()[1])
    mid_actual=r
    mid_temp=(r)-5
    w=device_folder[23:35]

    device_folder = glob.glob(base_dir + '28*') [2] #right
    device_file = device_folder + '/w1_slave'
    r=(read_temp()[1])
    right_actual=r
    right_temp=(r)-3

    y=device_folder[23:35]

    device_folder = glob.glob(base_dir + '28*') [3] #mudroom
    device_file = device_folder + '/w1_slave'
    r=(read_temp()[1])
    mudroom=(r)
    z=device_folder[23:35]

    device_folder = glob.glob(base_dir + '28*') [4] #left
    device_file = device_folder + '/w1_slave'
    r=(read_temp()[1])
    left_actual=r
    left_temp=(r)-1
    za=device_folder[23:35]


def do_ulo():
    fd_upper_left = open ("/run/shm/Upper_left_state", "w")
    fd_upper_left.write("Open")
    fd_upper_left.close()
    logging.debug(upper_left_open)
    os.system (upper_left_open)

def do_ulc():
    fd_upper_left = open ("/run/shm/Upper_left_state", "w")
    fd_upper_left.write("Closed")
    fd_upper_left.close()
    logging.debug(upper_left_close)
    os.system (upper_left_close)

def do_llo():
    fd_lower_left = open ("/run/shm/Lower_left_state", "w")
    fd_lower_left.write("Open")
    fd_lower_left.close()
    logging.debug(lower_left_open)
    os.system (lower_left_open)

def do_llc():
    fd_lower_left = open ("/run/shm/Lower_left_state", "w")
    fd_lower_left.write("Closed")
    fd_lower_left.close()
    logging.debug(lower_left_close)
    os.system (lower_left_close)

def do_umo():
    fd_upper_mid = open ("/run/shm/Upper_mid_state", "w")
    fd_upper_mid.write("Open")
    fd_upper_mid.close()
    logging.debug(upper_mid_open)
    os.system (upper_mid_open)

def do_umc():
    fd_upper_mid = open ("/run/shm/Upper_mid_state", "w")
    fd_upper_mid.write("Closed")
    fd_upper_mid.close()
    logging.debug(upper_mid_close)
    os.system (upper_mid_close)

def do_lmo():
    fd_lower_mid = open ("/run/shm/Lower_mid_state", "w")
    fd_lower_mid.write("Open")
    fd_lower_mid.close()
    logging.debug(lower_mid_open)
    os.system (lower_mid_open)

def do_lmc():
    fd_lower_mid = open ("/run/shm/Lower_mid_state", "w")
    fd_lower_mid.write("Closed")
    fd_lower_mid.close()
    logging.debug(lower_mid_close)
    os.system (lower_mid_close)

def do_uro():
    fd_upper_right = open ("/run/shm/Upper_right_state", "w")
    fd_upper_right.write("Open")
    fd_upper_right.close()
    logging.debug(upper_right_open)
    os.system (upper_right_open)

def do_urc():
    fd_upper_right = open ("/run/shm/Upper_right_state", "w")
    fd_upper_right.write("Closed")
    fd_upper_right.close()
    logging.debug(upper_right_close)
    os.system (upper_right_close)

def do_lro():
    fd_lower_right = open ("/run/shm/Lower_right_state", "w")
    fd_lower_right.write("Open")
    fd_lower_right.close()
    logging.debug(lower_right_open)
    os.system (lower_right_open)

def do_lrc():
    fd_lower_right = open ("/run/shm/Lower_right_state", "w")
    fd_lower_right.write("Closed")
    fd_lower_right.close()
    logging.debug(lower_right_close)
    os.system (lower_right_close)

def do_open_all():
    do_ulo()
    do_llo()
    do_umo()
    do_lmo()
    do_uro()
    do_lro()

def do_close_all():
    do_ulc()
    do_llc()
    do_umc()
    do_lmc()
    do_urc()
    do_lrc()



def display_web_page():

    # set up something to track current state of the left slot wall
    try:
        fd_upper_left = open ("/run/shm/Upper_left_state", "r")   # first check to see if already have existing state
    except IOError:
        fd_upper_left = open ("/run/shm/Upper_left_state", "w")   # if not, create new
        fd_upper_left.write("Open")
        fd_upper_left.close()
    fd_upper_left = open ("/run/shm/Upper_left_state", "r")
    Upper_left_state = fd_upper_left.read()
    fd_upper_left.close()

    try:
        fd_lower_left = open ("/run/shm/Lower_left_state", "r")   # first check to see if already have existing state
    except IOError:
        fd_lower_left = open ("/run/shm/Lower_left_state", "w")   # if not, create new
        fd_lower_left.write("Open")
        fd_lower_left.close()
    fd_lower_left = open ("/run/shm/Lower_left_state", "r")
    Lower_left_state = fd_lower_left.read()
    fd_lower_left.close()
    
    # set up something to track current state of the middle slot wall
    try:
        fd_upper_mid = open ("/run/shm/Upper_mid_state", "r")   # first check to see if already have existing state
    except IOError:
        fd_upper_mid = open ("/run/shm/Upper_mid_state", "w")   # if not, create new
        fd_upper_mid.write("Open")
        fd_upper_mid.close()
    fd_upper_mid = open ("/run/shm/Upper_mid_state", "r")
    Upper_mid_state = fd_upper_mid.read()
    fd_upper_mid.close()

    try:
        fd_lower_mid = open ("/run/shm/Lower_mid_state", "r")   # first check to see if already have existing state
    except IOError:
        fd_lower_mid = open ("/run/shm/Lower_mid_state", "w")   # if not, create new
        fd_lower_mid.write("Open")
        fd_lower_mid.close()
    fd_lower_mid = open ("/run/shm/Lower_mid_state", "r")
    Lower_mid_state = fd_lower_mid.read()
    fd_lower_mid.close()

    # set up something to track current state of the right slot wall
    try:
        fd_upper_right = open ("/run/shm/Upper_right_state", "r")   # first check to see if already have existing state
    except IOError:
        fd_upper_right = open ("/run/shm/Upper_right_state", "w")   # if not, create new
        fd_upper_right.write("Open")
        fd_upper_right.close()
    fd_upper_right = open ("/run/shm/Upper_right_state", "r")
    Upper_right_state = fd_upper_right.read()
    fd_upper_right.close()

    try:
        fd_lower_right = open ("/run/shm/Lower_right_state", "r")   # first check to see if already have existing state
    except IOError:
        fd_lower_right = open ("/run/shm/Lower_right_state", "w")   # if not, create new
        fd_lower_right.write("Open")
        fd_lower_right.close()
    fd_lower_right = open ("/run/shm/Lower_right_state", "r")
    Lower_right_state = fd_lower_right.read()
    fd_lower_right.close()


   
    fetch_temperatures()


    DayStamp = datetime.datetime.today().weekday()
    WeekDay = week[DayStamp]
    TimeStamp = datetime.datetime.now().strftime("%H:%M")


    webpage = open ( '/run/shm/index.html', 'w' )

    webpage.write ('''
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
"http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
<title>Therm</title>
<head><meta http-equiv="refresh" content="60"></head>

<body>
<form action="/slot_wall_mode.py" method="POST">
<table width="300" border="1">
  <tr>
    <td>&nbsp;<input type="submit" value="Submit"></td>
    <td>&nbsp;<input type="radio" name="Option" value="manual">manual</td>
    <td>&nbsp;<input type="radio" name="Option" value="auto">auto</td>
  </tr>
</table>
</form>
From pi@solwall.py: mudroom reference={:.1f}<br>
<table width="550" border="1" cellspacing="1" cellpadding="1">
  <tr>
    <td>pi@solwall</td>
    <td>day {:}</td>
    <td>time {:}</td>
    <td>mode {:} </td>
  </tr>
  <tr>
    <td>actual</td>
    <td>left  {:.1f}</td>
    <td>mid  {:.1f}</td>
    <td>right  {:.1f}</td>
  </tr>
  <tr>
    <td>virtual</td>
    <td>left  {:.1f}</td>
    <td>mid  {:.1f}</td>
    <td>right  {:.1f}</td>
  </tr>
    <tr>
    <td>upper state</td>
    <td>{:}</td>
    <td>{:}</td>
    <td>{:}</td>
  </tr>
  </tr>
    <tr>
    <td>lower state</td>
    <td>{:}</td>
    <td>{:}</td>
    <td>{:}</td>
  </tr>
  </table>
</body>
</html>'''.format(mudroom,WeekDay,TimeStamp,operating_mode,left_actual,mid_actual,right_actual,left_temp, \
        mid_temp,right_temp, \
        Upper_left_state, Upper_mid_state, Upper_right_state, \
        Lower_left_state, Lower_mid_state, Lower_right_state))

    webpage.close()



##############
# Begin MAIN #
##############

#print ("Number of command-line arguments: {:}".format(  len(sys.argv)  ))
if len(sys.argv) == 2:
    solo = sys.argv[1]
    if (solo == "-h") or (solo == "h"):
        print("""
        ca  = close all
        oa  = open all
        ulo = upper left open
        ulc = upper left close
        llo = lower left open
        llc = lower left close
        umo = upper middle open
        umc = upper middle close
        lmo = lower middle open
        lmc = lower middle close
        uro = upper right open
        urc = upper right close
        lro = lower right open
        lrc = lower right close
        """)
        sys.exit()
    if solo == "ca": #close all
        print ('sys.arg[1] = ca = close all')
        do_close_all()
        display_web_page()
        sys.exit()
    if solo == "oa": #open all
        print ('sys.arg[1] = oa = open all')
        do_open_all()
        display_web_page()
        sys.exit()
    if solo == "ulo": #upper left open
        print ('sys.arg[1] = ulo = upper left open')
        do_ulo()
        display_web_page()
        sys.exit()
    if solo == "ulc": #upper left close
        print ('sys.arg[1] = ulc = upper left close')
        do_ulc()
        display_web_page()
        sys.exit()
    if solo == "llo": #upper left open
        print ('sys.arg[1] = llo = lower left open')
        do_llo()
        display_web_page()
        sys.exit()
    if solo == "llc": #upper left close
        print ('sys.arg[1] = llc = lower left close')
        do_llc()
        display_web_page()
        sys.exit()
    if solo == "umo":
        print ('sys.arg[1] = umo = upper mid open')
        do_umo()
        display_web_page()
        sys.exit()
    if solo == "umc":
        print ('sys.arg[1] = umc = upper mid close')
        do_umc()
        display_web_page()
        sys.exit()
    if solo == "lmo":
        print ('sys.arg[1] = lmo = lower mid open')
        do_lmo()
        display_web_page()
        sys.exit()
    if solo == "lmc":
        print ('sys.arg[1] = lmc = lower mid close')
        do_lmc()
        display_web_page()
        sys.exit()
    if solo == "uro":
        print ('sys.arg[1] = uro = upper right open')
        do_uro()
        display_web_page()
        sys.exit()
    if solo == "urc":
        print ('sys.arg[1] = urc = upper right close')
        do_urc()
        display_web_page()
        sys.exit()
    if solo == "lro":
        print ('sys.arg[1] = lro = lower right open')
        do_lro()
        display_web_page()
        sys.exit()
    if solo == "lrc":
        print ('sys.arg[1] = lrc = lower right close')
        do_lrc()
        display_web_page()
        sys.exit()

operating_mode = "manual"
try:
    fd_operating_mode = open ("/run/shm/operating_mode", "r")
except IOError:
    operating_mode = "auto"
    
quarterly = "yes"
try:
    fd_quarterly = open ("/run/shm/run_quarterly_slot_wall", "r")    # see which flavor of output we need
except IOError:
    quarterly = "no"
if quarterly == "yes":
    os.system("shred /run/shm/run_quarterly_slot_wall -u")              # see you in 15 minutes
    





##########
#  left  #
##########

if left_temp > mudroom:
	logging.debug('left is hotter than mudroom, so opening left slots')
	if ("Closed" in left_slot_state): # no reason to open the slot it it's already opened
		left_slot_state = "Open"
		if quarterly=='yes':	
			do_ulo()
			do_llo()

else:
	logging.debug('left is colder than mudroom, closing left slots')
	if ("Open" in left_slot_state): # no reason to close the slot if it's already closed
		left_slot_state = "Closed"
		if quarterly=='yes':
			do_ulc()
			do_llc()
		fd_left = open ("/run/shm/left_state", "w")
		fd_left.write("Closed")
		fd_left.close()





############
#  middle  #
############

if mid_temp > mudroom:
	logging.debug('middle is hatter than mudroom, so opening middle slots')	
	if ("Closed" in mid_slot_state): # no reason to open the slot if it's already open
		mid_slot_state = "Open"
		if quarterly=='yes':
			do_umo
			do_lmo
		fd_mid = open ("/run/shm/mid_state", "w")
		fd_mid.write("Open")
		fd_mid.close()
		middle=('opened')
else:
	logging.debug('middle is colder than mudroom, so closing middle slots')
	if ("Open" in mid_slot_state): # no reason to close the slot if it's already closed
		mid_slot_state = "Closed"
		if quarterly=='yes':
			do_umc()
			do_lmc()
		fd_mid = open ("/run/shm/mid_state", "w")
		fd_mid.write("Closed")
		fd_mid.close()
		middle=('closed')




###########
#  right  #
###########

if right_temp > mudroom:
	logging.debug('right is hotter than mudroom, so opening right slotss')
	if ("Closed" in right_slot_state): # no reason to open the slot if it's already opened
		right_slot_state = "Open"
		if quarterly=='yes':
			do_uro()
			do_lro()
		fd_right = open ("/run/shm/right_state", "w")
		fd_right.write("Open")
		fd_right.close()
		right=('open')
else:
	logging.debug('right is colder than mudroom, so closing right slots')
	if ("Open" in right_slot_state): # no reason to close the slot if it's already closed
		right_slot_state = "Closed"	
		if quarterly=='yes':
			do_urc()
			do_lrc()
		fd_right = open ("/run/shm/right_state", "w")
		fd_right.write("Closed")
		fd_right.close()	
		right=('closed')

	

display_web_page()