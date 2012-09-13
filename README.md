# rogersusage.py
A python script to get internet usage data for customers of [Rogers][] cable internet.

## Requirements
 - [Python][python]. I have only tested this with 2.7.1 on OS X (the Apple supplied build) and 2.6.5 on Ubuntu. I'm not doing anything overly crazy, so chances are it will work on any relatively modern version, but I make no guarantees.
 - [mechanize][]. Install via `easy_install mechanize`, or download it yourself [here][mechanize dl].
 - [BeautifulSoup][] for HTML parsing. `easy_install BeautifulSoup`, or download from [the project site][soup dl].
 - A login for the [My Rogers][] site, used for managing your Rogers account.
 
## Usage
### Configuration
The script will prompt for your My Rogers login details, but if you prefer to, you can hard-code them in the script.
Open the script file in a text editor, and look for the lines with the login details:

    username = ''
    password = ''

Enter your user name and password between the quotes, then save the file.        

### Running the script
Open a command prompt, and run `python rogersusage.py`. You may need to adjust the paths to your python executable and the script as necessary.

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
