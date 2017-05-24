# imports
from __future__ import print_function, division
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime

import re # regular expressions
import requests

df = pd.read_csv('06-RTsouped.csv')
df = df.drop(df.columns[0], axis=1)
# Rename some columns
#BOMdf.rename(columns={'urlID':'urlID_bom', 'urlList':'url_bom', 'soupList':'soup_bom'}, inplace=True)
df.head()

df[df['url_rt']=="https://www.rottentomatoes.com"]

# Add some columns
df['scrap_rt'] = 0 # if we didn't run into scraping errors for T-N
df['title_rt'] = ''
df['rt_critic'] = 0.
df['rt_user'] = 0.

### Scraping through Rotten Tomatoes
# We'll try going through the first 100 or so movies, and see if we can parse all the info

i = 0


while i < len(df):
#while i < 10:

    # check if we're already finished with this one
    if df['scrap_rt'][i] == 1:
        if i >= 0:
        #if i >= 1499:
            print('Skipping: ', i, '...Already done.')
        i += 1
        continue

    print('Working on', i, df['title_rt'][i])
    
    # len=1 means we couldn't find the movie/url
    if len(str(df['soup_rt'][i])) < 5:
        df.set_value(i, 'rt_critic', 0.)
        df.set_value(i, 'rt_user', 0.)
    else:
        # Let's make some batches of soup from leftovers
        soup_rt = BeautifulSoup(df['soup_rt'][i])

        ### Title from Rotten Tomatoes ###

        end_i = soup_rt.find('title').text.find(' - Rotten Tomatoes') - 7
        title_rt = soup_rt.find('title').text[:end_i]
        df.set_value(i, 'title_rt', title_rt)

        ### Critics Rating from RT ###

        try:
            rt_critic = str(soup_rt.find(class_='col-sm-12 tomato-info hidden-xs').contents[1].contents[1])

            start_i = rt_critic.find('width:')
            end_i = rt_critic.find('%;"></div>')
            offset_i = len('width:')

            rt_critic = float(rt_critic[start_i+offset_i:end_i])/100
        except (AttributeError, ValueError) as e:
            rt_critic = 0.
        #print(rt_critic)
        df.set_value(i, 'rt_critic', rt_critic)

        ### User Rating from RT ###

        try:
            rt_user = soup_rt.find(class_='audience-score meter').find(class_='superPageFontColor').text
            rt_user = float(re.sub('[%]','',rt_user))/100
        except (AttributeError, ValueError) as e:
            rt_user = 0.
        #print(rt_user)
        df.set_value(i, 'rt_user', rt_user)


        ### ? ###

        df.set_value(i, 'scrap_rt', 1)
    
    i += 1
    #movie_i += 1
    
print('Done!')

# Let's get rid of unnecesary columns
df.drop(['url_bom','url_tn','2foundURL','scrap_tn','3foundURL','url_rt','soup_rt','scrap_rt'],axis=1,inplace=True)
df.columns

# Let's write this to another csv

df.to_csv('07-RTscraped.csv')