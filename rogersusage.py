#!/usr/bin/env python

# Rogers Internet Usage Parsing Script

import sys
import os
import re
import warnings
from getpass import getpass
import requests
from optparse import OptionParser, OptionGroup
from ConfigParser import SafeConfigParser

# try loading keyring module (https://bitbucket.org/kang/python-keyring-lib/)
try:
    import keyring
except ImportError:
    keyring_present = False
else:
    keyring_present = True

# ignore gzip warning
warnings.filterwarnings('ignore', 'gzip', UserWarning)

# define command line options
parser = OptionParser()
parser.add_option("-t", "--totals", action="store_true", dest="totals_only", help="Output only the total usage and usage allowance amounts.")
parser.add_option("--csv", action="store_true", dest="csv", help="Print the data only (no labels or units) as comma-separated values. Format: Download,Upload,Total,Cap Amount. Units: GB. Useful for importing or parsing the data into other programs.")
group = OptionGroup(parser, "Login Options", "If a login ID or password is provided, it will override any provided in the script file.")
group.add_option("-l", "--login", action="store", dest="username", help="Rogers login ID")
group.add_option("-p", "--password", action="store", dest="password", help="Rogers login password")
group.add_option("--no-save", action="store_true", dest="dont_save_login", help="Don't save login details")
parser.add_option_group(group)

# initialize user/pass
username = None
password = None

print_username_reminder = True

# parse command line options for login
(options, args) = parser.parse_args()
if options.username != None:
    username = options.username
    store_username = True
if options.password != None:
    password = options.password

# get username from config if it hasn't been loaded from command line
configfile = os.path.expanduser('~/.rogersusage_config')
userconfig = SafeConfigParser()

if username == None or username == '':
    userconfig.read(configfile)
    if userconfig.has_section('myrogers_login'):
        username = userconfig.get('myrogers_login', 'username')
        store_username = False
    else:
        #no username configured
        store_username = True

# get username interactively if it hasn't been loaded yet
if username == None or username == '':
    username = raw_input("Login ID: ")
    print_username_reminder = False

# get password from the keychain if possible
if password == None or password == '':
    if keyring_present:
        if keyring.get_password('myrogers_login', username) != None:
            password = keyring.get_password('myrogers_login', username)
            store_password = False
        else:
            store_password = True

# if password isn't in the keychain, get it interactively
if password == None or password == '':
    if  print_username_reminder:
        print "Login ID:", username

    password = getpass("Password: ")
    store_password = True

login_post_url = 'https://www.rogers.com/siteminderagent/forms/login.fcc'
login_post_data = {'USER': username, 'password': password, 'SMAUTHREASON': '0', 'target': '/web/RogersServices.portal/totes/#/accountOverview'}

auth_response = requests.post(login_post_url, data=login_post_data)

# check if login was successful
if 'SM_USERAUTHENTICATED' in auth_response.cookies.keys() and dict(auth_response.cookies)['SM_USERAUTHENTICATED'] == '1':
    # login was successful
    if not options.dont_save_login:
        if store_username:
            userconfig.add_section('myrogers_login')
            userconfig.set('myrogers_login', 'username', username)
            userconfig.write(open(configfile, 'w'))

        if keyring_present and store_password:
            keyring.set_password('myrogers_login', username, password)

elif 'SMTRYNO' in auth_response.cookies.keys():
    sys.exit("Login failed, bad username and/or password")
else:
    sys.exit("Login failed. Rogers may have changed their site and this script requires updating.")

# Get cookies from first load attempt
data_response = requests.get('https://www.rogers.com/web/myrogers/internetUsageBeta', cookies=auth_response.cookies)

# Manual redirect (Rogers uses Javascript redirects)
data_response = requests.get('https://www.rogers.com/web/myrogers/internetUsageBeta', cookies=data_response.cookies)


download_value = ''
upload_value = ''
usage_value = ''
cap_value = ''
remaining_value = cap_value - usage_value

if options.csv:
    output_string = str(usage_value) + "," + str(cap_value)

    if not options.totals_only:
        output_string = str(download_value) + "," + str(upload_value) + "," + output_string + "," + str(remaining_value)

    print output_string
else:
    if not options.totals_only:
        print download_value
        print upload_value
    print usage_value
    print cap_value
    if remaining_value < 0:
        print 'Overage:\n' + str(abs(remaining_value)) + ' GB'
    else:
        print 'Remaining Usage:\n' + str(remaining_value) + ' GB'
