# sky_epg_grab
Python script to pull up to seven days worth of EPG data directly from sky

Usage:

sky_epg_grab.py <filename> <number_of_days_to_grab> <tv_region>

filename - filename and path where to save the xml file

number_of_days_to_grab - number of days of epg to grab, 7 seems to be the maximum, pulling seven days of epg is around 20-22Mb of data

tv_region - this can be found be going to https://www.sky.com/tv-guide selecting your region in the drop down menu, once the region has loaded take a look at the url, at the end there will be the following number 4101-x where x is your region number.

Eg.

4101-1 - London HD
  
4101-2 - Essex HD

Prerequisites:

Python3+
  
cElementTree
  
BeautifulSoup
