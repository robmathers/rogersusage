#!/usr/bin/python

# Rogers Internet Usage Parsing Script

import sys
import os
import re
import warnings
from getpass import getpass
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup
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

# regex replacements
def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def remove_tabs(data):
    p = re.compile(r'\t')
    return p.sub('', data)

def remove_parens(data):
    p = re.compile(r'\(.*\)')
    return p.sub('', data)

def correct_space(data):
    p = re.compile(r'&nbsp;')
    return p.sub(' ', data)

def remove_units(data):
    p = re.compile(r' GB')
    return p.sub('', data)

def clean_output(data):
    data = str(data)
    data = remove_html_tags(data)
    data = remove_tabs(data)
    data = remove_parens(data)
    data = correct_space(data)
    data = os.linesep.join([s for s in data.splitlines() if s]) # remove empty lines
    return data

def detectLoginForm(session):
    for form in session.forms():
        for control in form.controls:
            if isinstance(control, mechanize._form.PasswordControl) and control.id == 'txtPassWord':
                return form

    return None

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

# mechanize boilerplate from http://stockrt.github.com/p/emulating-a-browser-in-python-with-mechanize/

# Browser
session = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
session.set_cookiejar(cj)

# Browser options
session.set_handle_equiv(True)
session.set_handle_gzip(True)
session.set_handle_redirect(True)
session.set_handle_referer(True)
session.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
session.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# Want debugging messages?
#session.set_debug_http(True)
#session.set_debug_redirects(True)
#session.set_debug_responses(True)

# end of mechanize set up

# open usage page (sets cookies and redirect for post-login)
session.open('https://www.rogers.com/web/myrogers/internetUsageBeta')

# manually redirect to sign in page
session.open('https://www.rogers.com/web/link/signin')

# login form
loginForm = detectLoginForm(session)
if loginForm is None:
    sys.exit("Could not find a login form. Rogers may have changed its site and an update to this app is required")

session.form = loginForm
session.form['USER'] = username
session.form['password'] = password
session.submit()

# check if login was successful
authent_cookies = [cookie for cookie in cj if cookie.name == 'SM_USERAUTHENTICATED']
if len(authent_cookies) == 0:
    sys.exit("Login failed")
else:
    # login was successful
    if not options.dont_save_login:
        if store_username:
            userconfig.add_section('myrogers_login')
            userconfig.set('myrogers_login', 'username', username)
            userconfig.write(open(configfile, 'w'))

        if keyring_present and store_password:
            keyring.set_password('myrogers_login', username, password)

# parse for usage data
soup = BeautifulSoup(session.response().read())
table = soup.find("table", {"id": "usageInformation"})

if table == None:
    print 'Could not get usage data. Please try again.'
    sys.exit(1)

download = table.findAll('tr')[1]
upload = table.findAll('tr')[2]
usage = table.findAll('tr')[3]
cap = table.findAll('tr')[4]

download_value = float(remove_units(clean_output(download.findAll('td')[1])))
upload_value = float(remove_units(clean_output(upload.findAll('td')[1])))
usage_value = float(remove_units(clean_output(usage.findAll('td')[1])))
cap_value = float(remove_units(clean_output(cap.findAll('td')[1])))
remaining_value = cap_value - usage_value

if options.csv:
    output_string = str(usage_value) + "," + str(cap_value)

    if not options.totals_only:
        output_string = str(download_value) + "," + str(upload_value) + "," + output_string + "," + str(remaining_value)

    print output_string
else:
    if not options.totals_only:
        print clean_output(download)
        print clean_output(upload)
    print clean_output(usage)
    print clean_output(cap)
    if remaining_value < 0:
        print 'Overage:\n' + str(abs(remaining_value)) + ' GB'
    else:
        print 'Remaining Usage:\n' + str(remaining_value) + ' GB'
