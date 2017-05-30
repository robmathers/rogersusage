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


def login(username, password):
    """Attempts a login and returns cookies."""
    login_url = "https://www.rogers.com/siteminderagent/forms/login.fcc"
    target_url = "https://www.rogers.com:/web/RogersServices.portal/totes/#/accountOverview"
    try:
        response = requests.post(
            url=login_url,
            data={
                "USER": username,
                "password": password,
                "target": target_url
            },
            allow_redirects=False
        )

        # Manually handle redirect to send cookies
        redirect_response = requests.get(
            url=response.next.url,
            cookies=response.cookies,
            allow_redirects=False
        )

        return redirect_response.cookies

    except requests.exceptions.RequestException:
        print('Login request failed')


def account_number(login_cookies):
    """
    Returns an account number mostly likely to be associated with an internet account.

    login_cookies: a CookieJar from requests with authenticated session cookies.
    """
    url = 'https://www.rogers.com/web/RogersServices.portal/totes/api/v1/accountoverview'

    try:
        response = requests.post(
            url=url,
            json={
                'refresh': False,
                'applicationId': 'Rogers.com'
            },
            cookies=login_cookies
        )

        if response.status_code == 200:
            account_info = response.json()
            return parse_account_number(account_info)
        else:
            print("Error getting account number")

    except requests.exceptions.RequestException:
        print("Error getting account number")

    return None

def parse_account_number(account_info):
    """
    Loops through sub-account numbers (phone and internet) to find the first possible internet account number.
    """
    for account in account_info['accountList']:
        for account_number in account['subNumbers']:
            # per Rogers error messages, valid account numbers should be 9 or 12 digits
            # helpfully this excludes phone numbers
            if len(account_number) == 9 or len(account_number) == 12:
                return account_number
    return None


def usage_data(account_number, login_cookies):
    """
    Returns a dictionary with usage data from Rogers.

    Dictionary keys: cap, download, upload, total, start_date, end_date.

    account_number: sub-account number for a Rogers Cable Internet subscription, distinct from the main billing account number.
    """

    url = 'https://www.rogers.com/web/RogersServices.portal/totes/api/v1/internetDashBoard/usage'

    try:
        response = requests.post(
            url=url,
            json={
                'accountNumber': account_number,
                'applicationId': 'Rogers.com'
            },
            cookies=login_cookies
        )

        if response.status_code == 200:
            try:
                usage_json = response.json()
                current_usage = usage_json['internetUsageToolVO']['currentUsageSummaryVO']

                usage = {
                    'cap': usage_json['internetUsageTotal'],
                    'download': current_usage['currentDownloadTotalUsage'],
                    'upload': current_usage['currentUploadTotalUsage'],
                    'total': usage_json['internetUsageUsed'],
                    'start_date': current_usage['currentBillPeriodStartDate'],
                    'end_date': current_usage['currentBillPeriodEndDate']
                }
                return usage
            except:
                print "Error parsing usage data. Rogers may have changed data formats. Please check for an update to rogersusage.py"
        else:
            print("Error getting usage data")

    except requests.exceptions.RequestException:
        print("Error getting usage data")

    return None


def main():
    """Main Function"""
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

    login_cookies = login(username, password)

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


if __name__ == '__main__':
    main()
