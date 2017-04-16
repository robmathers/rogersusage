# Currently Broken
An update in 2016 to Rogers site broke this script, due to inability to scrape properly.

# rogersusage.py
A python script to get internet usage data for customers of [Rogers][] cable internet.

## Requirements
 - [Python][python]. I have only tested this with 2.7.1 on OS X (the Apple supplied build) and 2.6.5 on Ubuntu. I'm not doing anything overly crazy, so chances are it will work on any relatively modern version, but I make no guarantees.
 - [requests][]. Installed via `pip install requests`, `easy_install` or from [source][requests source].
 - [BeautifulSoup][] for HTML parsing. `easy_install BeautifulSoup`, or download from [the project site][soup dl].
 - A login for the [My Rogers][] site, used for managing your Rogers account.
 - *Optional:* the [keyring][] library. If installed, the keyring will be used to securely store passwords. The storage mechanism depends on what OS you're running—on Mac OS X, it uses the system Keychain; read the keyring lib documentation for full details.

## Usage
### Running the script
Open a command prompt, and run `python rogersusage.py`. Provide the full paths to the python executable and the script as necessary.

### Configuration
The script will prompt for a My Rogers login ID (typically an email address) and password. You can also provide one with the command line parameters: `-l USERNAME` (or `--login=USERNAME`) and `-p PASSWORD` (or `--password=PASSWORD`). These will supersede any stored login details.

 Upon a successful login, the script stores the login ID for later use. If the keyring library is installed, it will also securely store your password. This behaviour can be disabled by using the `--no-save` option.

### Options
 - `-h`, `--help`
    - Print a help message with a description of the options
 - `-t`, `--totals`
    - Output only the total usage and usage allowance amounts.
 - `--csv`
    - Print the data only (no labels or units) as comma-separated values. Format: Download,Upload,Total,Cap Amount,Remaining Usage. Units: GB. Useful for importing or parsing the data into other programs.
 - `-l USERNAME`, `--login=USERNAME`
    - Rogers login ID
 - `-p PASSWORD`, `--password=PASSWORD`
    - Rogers login password
 - `--no-save`
    - Don't save login details

### Sample Output
    Download Usage:
    50.38 GB
    Upload Usage:
    11.26 GB
    Total Usage:
    61.64 GB
    Usage Allowance:
    120 GB
    Remaining Usage:
    58.36 GB

## Notes
This is provided as-is, with no warranty or guarantee of any kind it will work. Hopefully someone else will find it useful. It's scraping HTML to get the data, so it will likely break if Rogers makes changes to their site.

[BeautifulSoup]: http://www.crummy.com/software/BeautifulSoup/
[soup dl]: http://www.crummy.com/software/BeautifulSoup/#Download
[python]: http://www.python.org/
[rogers]: http://www.rogers.com
[my rogers]: https://www.rogers.com/web/RogersServices.portal?_nfpb=true&amp;_pageLabel=My%20Rogers_Home
[requests]: http://docs.python-requests.org/en/latest/
[requests source]: https://github.com/kennethreitz/requests
[keyring]: https://bitbucket.org/kang/python-keyring-lib/
