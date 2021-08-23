import sys
import requests
import json
import time
import xml.etree.cElementTree as ET
from itertools import islice
from bs4 import BeautifulSoup

def get_channel_names(channel_name_uri):
    page = requests.get(channel_name_uri)

    soup = BeautifulSoup(page.content, "html.parser")
    channels = {}
    results = soup.find(id="article_body").find_all("p")
    # test_string = ("  BBC Radio Cymru 2 (England, Scotland and Northern Ireland)").split("(")[0].strip()

    # print(test_string)
    for strong_tag in soup.find_all('strong'):

        if ":" in strong_tag.text:
            if " " not in strong_tag.text:
                channel_number = strong_tag.text.split(":")[0].strip()
                channel_name = strong_tag.next_sibling.split("(")[0].strip()
                channel_details = [channel_name, "", ""]
                channels[channel_number] = channel_details
    return(channels)

def get_channel_details(channel_details_uri, channel_names):
    sky_channel_details = json.loads(requests.get(channel_details_uri).content)
    for sky_channel_detail in sky_channel_details['services']:
    
        sid = sky_channel_detail["sid"]
        channel_number = sky_channel_detail["c"]
        channel_title = sky_channel_detail["t"]
        for key, value in channel_names.items():
            if channel_number == key:
                channel_names[channel_number][1] = channel_title
                channel_names[channel_number][2] = sid
    return(channel_names)

def open_xml():
    root = ET.Element("tv")
   
    return(root)    

def write_xml(root, filename):
    tree = ET.ElementTree(root)
    tree.write(filename)      
        
def write_channel_xml(root, channel_details):
    
    for channel_detail in channel_details:
        channel_xml = ET.SubElement(root, 'channel')
        channel_xml.set('id',channel_details[channel_detail][2])
        ET.SubElement(channel_xml, "display-name").text = channel_details[channel_detail][0]
        ET.SubElement(channel_xml, "display-name").text = channel_details[channel_detail][1]
        ET.SubElement(channel_xml, "display-name").text = channel_detail
        icon_uri = "https://d2n0069hmnqmmx.cloudfront.net/epgdata/1.0/newchanlogos/10000/10000/skychb{}.png".format(channel_details[channel_detail][2]) 
        channel_icon = ET.SubElement(channel_xml, "icon")
        channel_icon.set('src', icon_uri)
        
    return(root)
        
def get_listings(uri):
    days_listings = json.loads(requests.get(uri).content)
    
    return(days_listings)

def programs(days_listings, root):
    
    for schedule in (days_listings['schedule']):
        channel_id = (schedule['sid'])
        for program in (schedule['events']):
            
            start_time = time.strftime('%Y%m%d%H%M', time.localtime(program['st']))
            end_time = time.strftime('%Y%m%d%H%M', time.localtime(program['st'] + program['d']))

            program_xml = ET.SubElement(root, 'programme')
            program_xml.set('start',start_time)
            program_xml.set('stop',end_time)
            program_xml.set('channel',channel_id)
            ET.SubElement(program_xml, "title").text = (program['t'])
            if 'sy' in program:
                ET.SubElement(program_xml, "desc").text = (program['sy'])
                
    
    return(root)

def chunks(data, SIZE=10000):
   it = iter(data)
   for i in range(0, len(data), SIZE):
      yield {k:data[k] for k in islice(it, SIZE)}

def get_epg_uris(channel_details, root, days):      
    for sids in chunks(channel_details, 10):
        list_of_sids =[]
   
        for key, value in sids.items():
            if(value[2]):
                list_of_sids.append(value[2])
            string_of_sids = ','.join(list_of_sids)
    
        date = time.strftime('%Y%m%d', time.localtime())
        for x in range(days):
            listing_day = (int(date)+x)
            epg_uri = 'https://awk.epgsky.com/hawk/linear/schedule/{}/{}'.format(listing_day,string_of_sids)
            day_listings = get_listings(epg_uri)
            root = programs(day_listings, root)

def get_sky_epg_data(filename, days, region):            
    channel_name_uri = "https://www.mediamole.co.uk/entertainment/broadcasting/information/sky-full-channels-list-epg-numbers-and-local-differences_441957.html"
    channel_names = (get_channel_names(channel_name_uri))

    channel_details_uri = "https://awk.epgsky.com/hawk/linear/services/4101/{}".format(region)
    channel_details = (get_channel_details(channel_details_uri, channel_names))

    root = open_xml()

    root = write_channel_xml(root, channel_details)

    get_epg_uris(channel_details, root, days)

    write_xml(root, filename)
    print(ET.tostring(root, encoding="unicode"))

if __name__ == "__main__":
    
    if (len(sys.argv) == 4) and (sys.argv[2].isdigit()) and (int(sys.argv[2]) < 8) and (sys.argv[3].isdigit()):
        filename = sys.argv[1]
        days = int(sys.argv[2])
        region = int(sys.argv[3])
        
        get_sky_epg_data(filename, days, region)
    else:
        print ("Wrong Syntax")
        print ("sky_epg_grab.py <filename> <number_of_days_to_grab> <tv_region")
        print ("number_of_days_to_grab must be less than 8 days")
