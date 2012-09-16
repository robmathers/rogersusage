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

# define command line options
parser = OptionParser()
parser.add_option("-t", "--totals", action="store_true", dest="totals_only", help="Output only the total usage and usage allowance amounts.")
parser.add_option("--csv", action="store_true", dest="csv", help="Print the data only (no labels or units) as comma-separated values. Format: Download,Upload,Total,Cap Amount. Units: GB. Useful for importing or parsing the data into other programs.")
group = OptionGroup(parser, "Login Options", "If a login ID or password is provided, it will override any provided in the script file.")
group.add_option("-l", "--login", action="store", dest="username", help="Rogers login ID")
group.add_option("-p", "--password", action="store", dest="password", help="Rogers login password")
parser.add_option_group(group)

# initialize user/pass
username = None
password = None

# parse command line options for login
(options, args) = parser.parse_args()
if options.username != None:
    username = options.username
    write_configfile = True
if options.password != None:
    password = options.password
    
# get username from config if it hasn't been loaded from command line
configfile = 'myrogers_config'
userconfig = SafeConfigParser()

if username == None:
    userconfig.read(configfile)
    if userconfig.has_section('myrogers_login'):
        username = userconfig.get('myrogers_login', 'username')
        write_configfile = False
    else:
        #no username configured
        write_configfile = True

# get login details interactively if they haven't been hard-coded
if username == None or username == '':
    username = raw_input("Login ID: ")
elif password == None or password == '':    # print a username reminder if a login id was provided
    print "Login ID:", username             # but a password was not

if  password == None or password == '':
    password = getpass("Password: ")

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
session.select_form(nr=2)
session.form['USER'] = username
session.form['password'] = password
session.submit()

# check if login was successful
authent_cookies = [cookie for cookie in cj if cookie.name == 'SM_USERAUTHENTICATED']
if len(authent_cookies) == 0:
    sys.exit("Login failed")    
else:
    # login was successful
    if write_configfile:
        userconfig.add_section('myrogers_login')
        userconfig.set('myrogers_login', 'username', username)
        userconfig.write(open(configfile, 'w'))
    pass

# parse for usage data
soup = BeautifulSoup(session.response().read())
table = soup.find("table", {"id": "usageInformation"})

download = table.findAll('tr')[1]
upload = table.findAll('tr')[2]
usage = table.findAll('tr')[3]
cap = table.findAll('tr')[4]

if options.csv:
    download_value = remove_units(clean_output(download.findAll('td')[1]))
    upload_value = remove_units(clean_output(upload.findAll('td')[1]))
    usage_value = remove_units(clean_output(usage.findAll('td')[1]))
    cap_value = remove_units(clean_output(cap.findAll('td')[1]))
    
    output_string = usage_value + "," + cap_value
    
    if not options.totals_only:
        output_string = download_value + "," + upload_value + "," + output_string
        
    print output_string
else:
    if not options.totals_only:
        print clean_output(download)
        print clean_output(upload)
    print clean_output(usage)
    print clean_output(cap)
