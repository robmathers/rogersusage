# rogersusage.py
A python script to get internet usage data for customers of [Rogers](http://www.rogers.com) cable internet.

## Requirements
 - [Python](http://www.python.org/). I have only tested this with 2.7.1 on OS X (the Apple supplied build) and 2.6.5 on Ubuntu. I'm not doing anything overly crazy, so chances are it will work on any relatively modern version, but I make no guarantees.
 - [mechanize](http://wwwsearch.sourceforge.net/mechanize/). Install via `easy_install mechanize`, or download it yourself [here](http://wwwsearch.sourceforge.net/mechanize/download.html).
 - [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/) for HTML parsing. `easy_install BeautifulSoup`, or download from [the project site](http://www.crummy.com/software/BeautifulSoup/#Download).
 - A login for the [MyRogers](https://www.rogers.com/web/RogersServices.portal?_nfpb=true&amp;_pageLabel=MyRogers_Home) site, used for managing your Rogers account.
 
## Usage
### Configuration
Currently the script uses hard-coded login details (I plan on changing this in the future). Before running it, open it in a text editor and replace `SOMEUSER` and `SOMEPASS` with your MyRogers login information. Make sure to retain the quotes around them.

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
