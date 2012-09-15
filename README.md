# rogersusage.py
A python script to get internet usage data for customers of [Rogers][] cable internet.

## Requirements
 - [Python][python]. I have only tested this with 2.7.1 on OS X (the Apple supplied build) and 2.6.5 on Ubuntu. I'm not doing anything overly crazy, so chances are it will work on any relatively modern version, but I make no guarantees.
 - [mechanize][]. Install via `easy_install mechanize`, or download it yourself [here][mechanize dl].
 - [BeautifulSoup][] for HTML parsing. `easy_install BeautifulSoup`, or download from [the project site][soup dl].
 - A login for the [My Rogers][] site, used for managing your Rogers account.
 
## Usage
### Running the script
Open a command prompt, and run `python rogersusage.py`. Provide the full paths to the python executable and the script as necessary.

### Configuration
The script needs the My Rogers login ID (typically an email address) and password, which can be provided in one of three ways:

1. Command line parameters. `-l USERNAME` (or `--login=USERNAME`) and `-p PASSWORD` (or `--password=PASSWORD`). These will override any login details provided in the script file.
2. In the script file. Open `rogersusage.py` in a text editor, and look for the lines with the login details:

        username = ''
        password = ''

    Enter your user name and password between the quotes, then save the file.
3. Interactively. If the script is not provided login details, it will prompt for them when run.

### Options
 - `-h`, `--help`
    - Print a help message with a description of the options
 - `-t`, `--totals`
    - Output only the total usage and usage allowance amounts.
 - `--csv`
    - Print the data only (no labels or units) as comma-separated values. Format: Download,Upload,Total,Cap Amount. Units: GB. Useful for  importing or parsing the data into other programs.
 - `-l USERNAME`, `--login=USERNAME`
    - Rogers login ID
 - `-p PASSWORD`, `--password=PASSWORD`
    - Rogers login password

### Sample Output
    Download Usage:
    50.38 GB
    Upload Usage:
    11.26 GB
    Total Usage:
    61.64 GB
    Usage Allowance:
    120 GB

## Notes
This is provided as-is, with no warranty or guarantee it will work of any kind. Hopefully someone else will find it useful. It's scraping HTML to get the data, so it will likely break if Rogers makes changes to their site.

[BeautifulSoup]: http://www.crummy.com/software/BeautifulSoup/
[soup dl]: http://www.crummy.com/software/BeautifulSoup/#Download
[python]: http://www.python.org/
[rogers]: http://www.rogers.com
[my rogers]: https://www.rogers.com/web/RogersServices.portal?_nfpb=true&amp;_pageLabel=My%20Rogers_Home
[mechanize]: http://wwwsearch.sourceforge.net/mechanize/
[mechanize dl]: http://wwwsearch.sourceforge.net/mechanize/download.html
