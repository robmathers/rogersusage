#!/usr/bin/python

# Rogers Internet Usage Parsing Script

# **Enter login details here**
username = ''
password = ''

import os
import re
import warnings
from getpass import getpass
import mechanize
import cookielib
from BeautifulSoup import BeautifulSoup

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

def clean_output(data):
    data = str(data)
    data = remove_html_tags(data)
    data = remove_tabs(data)
    data = remove_parens(data)
    data = correct_space(data)
    data = os.linesep.join([s for s in data.splitlines() if s]) # remove empty lines
    return data

# get login details interactively if they haven't been hard-coded
if username == '' or password == '':
    username = raw_input("Login ID: ")
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

# parse for usage data
soup = BeautifulSoup(session.response().read())
table = soup.find("table", {"id": "usageInformation"})

download = table.findAll('tr')[1]
upload = table.findAll('tr')[2]
usage = table.findAll('tr')[3]
cap = table.findAll('tr')[4]

print clean_output(download)
print clean_output(upload)
print clean_output(usage)
print clean_output(cap)
