# imports
from __future__ import print_function, division
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime

import re # regular expressions
import requests

df = pd.read_csv('05-TNdone-nosouptn.csv')
df = df.drop(df.columns[0], axis=1)
# Rename some columns
#BOMdf.rename(columns={'urlID':'urlID_bom', 'urlList':'url_bom', 'soupList':'soup_bom'}, inplace=True)
df.head()

# Pass the BOM title and release date to try to find the link at RT
# Returns None if not found
# Returns '0' if there's an error in making the soup
# Otherwise returns the URL
def findRTurl(title, reldate):
    
    if len(title) < 2:
        print('too small')
        return None
    
    import re
    from datetime import datetime
    import pandas as pd
    
    reldate = pd.to_datetime(reldate)
    
    relyear = reldate.year
    
    search_start = 'https://www.rottentomatoes.com/search/?search='
    
    # Get rid of any unwanted characters
    title_s = re.sub("[,']",'',title)
    title_s = re.sub("[:]",' ',title_s)
    title_s = re.sub("[ ]",'%20',title_s)
    
    search = search_start + title_s
    
    #return title_s
    
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
    
    try:
        results = str(search_soup.find(id = 'search-results-root').findNextSibling().contents[0])
    except AttributeError:
        return None
    
    if results == None:
        # No results found
        print(title_s, '->', title_s[:-2])
        return findRTurl(title_s[:-2],reldate)
    else:
        year_i = results.find('"year":' + str(relyear))
        if year_i < 0:
            # No result for year found
            print(title_s, '->', title_s[:-2])
            return findRTurl(title_s[:-2],reldate)
        else:
            # The year exists, so we'll chop until we get the url alone
            
            results = results[year_i:]
            end_i = results.find('{"castItems')
            results = results[:end_i]
            results = results[:-3]
            #print(results)
            start_i = results.find('url')+6
            results = results[start_i:]
            #print(results)
            #print(title, results.find('"}],"franchise'))
            
            # other url catching
            end_i = results.find('"}],"franchise')
            if end_i > 0:
                results = results[:end_i+1]
            
            end_i = results.find("},{")
            if end_i > 0:
                results = results[:end_i-1]
                
            end_i = results.find('"}],')
            if end_i > 0:
                results = results[:end_i]
            #return results
    
    url_rt = "https://www.rottentomatoes.com" + results
    
    return url_rt

# Add some columns
df['3success'] = 0 # if we didn't run into soup making errors for RT
df['3foundURL'] = 0 # if we found the url for RT
df['url_rt'] = ''
df['soup_rt'] = ''

# start at 0
i = 0

#while i < 10:
while i < len(df):
    
    urlError = False
    # check if we're already finished with this one
    if df['3success'][i] == 1:
        if i > 2200:
            print('Skipping: ', i, '...Already done.')
        i += 1
        continue
        
    urlSearch = findRTurl(df['title_bom'][i], df['reldate_bom'][i])
    
    if urlSearch == None:
        df.set_value(i, 'url_rt', urlSearch)
        df.set_value(i, '3success', 1)
        df.set_value(i, '3foundURL', 0)
        print('URL not found:', 'i=' + str(i), df['title_bom'][i])
    else:
        if len(urlSearch) > 10:
            df.set_value(i, 'url_rt', urlSearch)
            df.set_value(i, '3foundURL', 1)

            
            
            if len(urlSearch) > 100:
                
                url_end_i = urlSearch.find("},{") + 1
                if url_end_i < 0:
                    print("URL not fxnl:", urlSearch)
                    urlError = True
                
                urlSearch = urlSearch[:url_end_i]

            if len(urlSearch) > 0 and urlSearch[-1] == '"':
                urlSearch = urlSearch[:-1]
            
            ################
            # I don't remember what this conditional was for....
            if i == i:
                urlSearch = urlSearch.strip()
                # Making some soup
                try:
                    response = requests.get(urlSearch)
                    response_code = response.status_code
                    page = response.text
                    rt_soup = BeautifulSoup(page)
                    # Add to df
                    df.set_value(i, 'soup_rt', rt_soup)
                except:
                    urlError = True
                
                if response_code > 399 or urlError:
                    print('Error with test access:', response_code, 'i=' + str(i), df['title_bom'][i], urlSearch)
                    df.set_value(i, '3success', 0)
                else:
                    df.set_value(i, '3success', 1)
                    print('Done with:', i)
            
            #print('Unable to make soup from:', df['title_bom'][i])
                
#             try:
#                 if i == i:
#                     # Making some soup
#                     response = requests.get(urlSearch)
#                     response_code = response.status_code
#                     if response_code > 399:
#                         print('Error with test access:', response_code)
#                     page = response.text
#                     rt_soup = BeautifulSoup(page)

#                     # Add to df
#                     BOMdf.set_value(i, 'soup_rt', rt_soup)
#                     BOMdf.set_value(i, '3success', 1)
            
#             except:
#                 print('Unable to make soup from:', df['title_bom'][i])
    
    
    i += 1
    
print("Done!")

# Let's write this to another csv

df.to_csv('06-RTsouped.csv')