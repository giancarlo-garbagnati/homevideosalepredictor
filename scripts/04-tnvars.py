# imports
from __future__ import print_function, division
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime

import re # regular expressions
import requests

BOMdf = pd.read_csv('04-TNdone-nosoupbom.csv')
# Get rid of the extra index column
BOMdf = BOMdf.drop(BOMdf.columns[0], axis=1)
# Rename some columns
#BOMdf.rename(columns={'urlID':'urlID_bom', 'urlList':'url_bom', 'soupList':'soup_bom'}, inplace=True)
BOMdf.head()

# Let's write this to a second csv

BOMdf.to_csv('04-TNdone-nosoupbom.csv')

df = pd.read_csv('04-TNdone-nosoupbom.csv')
df = df.drop(df.columns[0], axis=1)
# Rename some columns
#BOMdf.rename(columns={'urlID':'urlID_bom', 'urlList':'url_bom', 'soupList':'soup_bom'}, inplace=True)
df.head()

# Add some columns
df['scrap_tn'] = 0 # if we didn't run into scraping errors for T-N
df['title_tn'] = ''
df['reldate_tn'] = ''
df['runtime_tn'] = 0
df['prodbud'] = 0
df['vidrel'] = ''
df['totalvid'] = 0
df['dvd8wk'] = 0
df['blu8wk'] = 0

### Scraping through The-Numbers
# We'll try going through the first 100 or so movies, and see if we can parse all the info

i = 0


while i < len(df):
    
    # check if we're already finished with this one
    if df['scrap_tn'][i] == 1:
        print('Done with:', i)
        i += 1
        continue

    print(i)
    # Let's make some batches of soup from leftovers
    if isinstance(df['soup_tn'][i], str):
        soup = BeautifulSoup(df['soup_tn'][i])
    else:
        df.set_value(i, 'scrap_tn', 1)
        i += 1
    # Mini Soup for scraping Release Date/Budget/Runtime from T-N
    soup_tn_2 = BeautifulSoup(soup.find(text=re.compile('Movie Details')).parent.findNextSibling().text)
    # Financials tab soup
    if isinstance(df['soup_tn_f'][i], str):
        soup_tn_f = BeautifulSoup(df['soup_tn_f'][i])
    else:
        df.set_value(i, 'scrap_tn', 1)
    #THE-NUMBERS - VIDEO-SALES SUBSECTION
    soup_tn_f_2 = soup_tn_f.find(id='video-sales')
    
    ### Title ###
    
    title_tn = soup.find('h1',{'itemprop':'name'}).text
    df.set_value(i, 'title_tn', title_tn)
    
    ### Production Budget ###
    
    start_i = soup_tn_2.text.find('Budget:$')
    end_i = soup_tn_2.text.find('\nDomestic')
    offset_i = len('Budget:$')

    prodbud = soup_tn_2.text[start_i+offset_i:end_i]

    try:
        prodbud = float(re.sub('[,$]','',prodbud))
    except ValueError:
        print('ValueError:', i, title_tn, 'prodbud')
        prodbud = 0

    df.set_value(i, 'prodbud', prodbud)
    
    ##### The-Numbers Financials Tab #####
    
    ### Total Video Numbers ###
    
    totalvid = soup_tn_f.find('table', {'id':'movie_finances'}).text

    start_i = totalvid.find('Total Domestic Video Sales')
    offset_i = len('Total Domestic Video Sales') + 1
    end_i = totalvid.find('Further financial details') - 2

    totalvid = totalvid[start_i+offset_i:end_i]

    try:
        #print(title_tn)
        totalvid = int(re.sub('[$,]','',totalvid))
    except ValueError:
        print('ValueError:', i, title_tn, 'totalvid')
        totalvid = 0
    
    df.set_value(i, 'totalvid', totalvid)
    
    ### Total $ Sales for DVDs after 8 weeks ###
    
    video_sales = soup_tn_f_2

    try:
        dvd_table = video_sales.find_all(id='box_office_chart')[0].contents[1]
        end_bound = len(dvd_table.contents)
        j = 3
        while j < end_bound:
            perchange_i = 3
            total_spend_i = 6
            weeks_rel_i = 7
            dvd8wk = 0

            # check if there's a % change, if so shift the other two indices over by 1
            if '%' in dvd_table.contents[j].contents[perchange_i].text:
                total_spend_i += 1
                weeks_rel_i += 1

            if int(dvd_table.contents[j].contents[weeks_rel_i].text) > 8:
                dvd8wk = 0
                break
            if int(dvd_table.contents[j].contents[weeks_rel_i].text) == 8:
                dvd8wk = dvd_table.contents[j].contents[total_spend_i].text
                break
            j += 2
    except IndexError:
        print('IndexError:', i, title_tn, 'dvd8wk')
        dvd8wk = 0

    #print(dvd8wk)
    dvd8wk = str(dvd8wk)
    dvd8wk = int(re.sub('[$,]','',dvd8wk))    

    df.set_value(i, 'dvd8wk', dvd8wk)
    
    ### Total $ Sales for blu-rays after 8 weeks ###

    try:
        blu_table = video_sales.find_all(id='box_office_chart')[1].contents[1]

        end_bound = len(blu_table.contents)
        j = 3
        while j < end_bound:
            perchange_i = 3
            total_spend_i = 6
            weeks_rel_i = 7
            blu8wk = 0

            # check if there's a % change, if so shift the other two indices over by 1
            if '%' in blu_table.contents[j].contents[perchange_i].text:
                total_spend_i += 1
                weeks_rel_i += 1

            #print(blu_table.contents[i].contents[weeks_rel_i].text)

            if int(blu_table.contents[j].contents[weeks_rel_i].text) > 8:
                blu8wk = 0
                break
            if int(blu_table.contents[j].contents[weeks_rel_i].text) == 8:
                blu8wk = blu_table.contents[j].contents[total_spend_i].text
                break
            j += 2
    except IndexError:
        print('IndexError:', i, title_tn, 'blu8wk')
        blu8wk = '0'

    #print(title_tn, blu8wk)
    blu8wk = str(blu8wk)
    blu8wk = int(re.sub('[$,]','',blu8wk))    

    df.set_value(i, 'blu8wk', blu8wk)
    
    
    
    ### ? ###
    
    df.set_value(i, 'scrap_tn', 1)
    
    i += 1
    #movie_i += 1

# Let's get rid of the used soups
df.drop(['soup_tn', 'soup_tn_f'], axis=1, inplace=True)
df.columns

# Get rid of the unused columns
df.drop(['reldate_tn','runtime_tn','vidrel'], axis=1, inplace=True)
df.columns

# Let's write this to another csv

df.to_csv('05-TNdone-nosouptn.csv')

