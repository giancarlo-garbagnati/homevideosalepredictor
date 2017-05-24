# imports
from __future__ import print_function, division
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime

import re # regular expressions
import requests

BOMdf = pd.read_csv('03-BOMdone.csv')
# Get rid of the extra index column
BOMdf = BOMdf.drop(BOMdf.columns[0], axis=1)
# Rename some columns
#BOMdf.rename(columns={'urlID':'urlID_bom', 'urlList':'url_bom', 'soupList':'soup_bom'}, inplace=True)
BOMdf.head()

# Pass the BOM title and release date to try to find the link at T-N
# Returns None if not found
# Returns '0' if there's an error in making the soup
# Otherwise returns the URL
def findTNurl(title, reldate):
    
    if len(title) < 2:
        print('too small')
        return None
    
    import re
    from datetime import datetime
    import pandas as pd
    
    search_start = 'http://www.the-numbers.com/search?searchterm='
    search_end = '&searchtype=allmatches'
    
    # Get rid of any unwanted characters
    title_s = re.sub("[,]",'',title)
    title_s = re.sub("[']",'%27',title)
    title_s = re.sub("[:]",' ',title_s)
    title_s = re.sub("[ ]",'+',title_s)
    
    search = search_start + title_s + search_end
    
    try:
        # Making some soup
        response = requests.get(search)
        response_code = response.status_code
        if response_code > 399:
            print('Error with test access:', response_code)
        page = response.text
        search_soup = BeautifulSoup(page)
    except:
        print('Unable to make soup from:', title)
        return '0'
    
    
    if search_soup.find_all('option')[1].parent.parent.parent.parent.parent.parent.findNextSibling().contents[1].text != 'Movies':
        # No results found
        print(title_s[:-2])
        return findTNurl(title_s[:-2],reldate)
    else:
        #print('we have some results')
        table = search_soup.find_all('option')[1].parent.parent.parent.parent.parent.parent.findNextSibling().contents[3]
        # First item
        #table.contents[1].contents[3]

        # Setting the date bounds
        date1 = '4/1/2015'
        date2 = '3/1/2015'
        date1 = datetime.strptime(date1,'%m/%d/%Y')
        date2 = datetime.strptime(date2,'%m/%d/%Y')
        posDateBound = date1 - date2
        negDateBound = date2 - date1

        i = 3
        # just an upper bounds to search through the search results (top 7 results)
        i_end = 3 + (2*7)
        
        while i < len(table.contents[1].contents) and i < i_end:
            date = table.contents[1].contents[i].text
            
            # clean the date string and convert it to datetime
            start_i = date.find('\n') + 1
            date = date[start_i:]
            end_i = date.find('\n')
            date = date[:end_i]
            date = datetime.strptime(date,'%m/%d/%Y')
            
            reldate = pd.to_datetime(reldate)
            
            if reldate > date:
                print( reldate - date )
                if reldate - date < posDateBound:
                    url_tn = 'http://www.the-numbers.com' + table.contents[1].contents[3].contents[4].find('a')['href']
                    return url_tn
            else:
                print (date - reldate )
                if date - reldate < posDateBound:
                    url_tn = 'http://www.the-numbers.com' + table.contents[1].contents[3].contents[4].find('a')['href']
                    return url_tn

            i += 2

        return findTNurl(title_s[:-2],reldate)
    
    #'No movie match found'
    # We shouldn't be here?
    return None
    

# add some columns

BOMdf['2success'] = 0 # if we didn't run into soup making errors
BOMdf['2foundURL'] = 0 # if we found the url
BOMdf['url_tn'] = ''
BOMdf['soup_tn'] = ''
BOMdf['soup_tn_f'] = ''

# start at 0
i = 0

#while i < 10:
while i < len(BOMdf):
    
    # check if we're already finished with this one
    if BOMdf['2success'][i] == 1:
        i += 1
        continue
        
    urlSearch = findTNurl(BOMdf['title_bom'][i], BOMdf['reldate_bom'][i])
    
    if urlSearch == None:
        BOMdf.set_value(i, 'url_tn', urlSearch)
        BOMdf.set_value(i, '2success', 1)
        BOMdf.set_value(i, '2foundURL', 0)
    else:
        if len(urlSearch) > 10:
            BOMdf.set_value(i, 'url_tn', urlSearch)
            BOMdf.set_value(i, '2foundURL', 1)

            try:
                if i == i:
                    # Making some soup
                    response = requests.get(urlSearch)
                    response_code = response.status_code
                    if response_code > 399:
                        print('Error with test access:', response_code)
                    page = response.text
                    tn_soup = BeautifulSoup(page)

                    # Get T-N-F soup
                    url_tn_f = urlSearch[:-7] + 'video-sales'
                    print(url_tn_f)
                    response = requests.get(url_tn_f)
                    response_code = response.status_code
                    if response_code > 399:
                        print('Error with test access:', response_code)
                    page = response.text
                    tnf_soup = BeautifulSoup(page)

                    # Add to df
                    BOMdf.set_value(i, 'soup_tn', tn_soup)
                    BOMdf.set_value(i, 'soup_tn_f', tnf_soup)
                    BOMdf.set_value(i, '2success', 1)
            
            except:
                print('Unable to make soup from:', BOMdf['title_bom'][i])
    
    
    i += 1

# Let's write this to a csv

BOMdf.to_csv('04-TNdone.csv')