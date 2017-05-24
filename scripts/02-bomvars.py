# imports
from __future__ import print_function, division
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import datetime

import re # regular expressions
import requests


BOMdf = pd.read_csv('02-BOMlinks_200per.csv')
# Get rid of the extra index column
BOMdf = BOMdf.drop(BOMdf.columns[0], axis=1)
# Rename some columns
BOMdf.rename(columns={'urlID':'urlID_bom', 'urlList':'url_bom', 'soupList':'soup_bom'}, inplace=True)
BOMdf.head()

# Let's add some all the necessary columns for this site
BOMdf['1success'] = 1 # if parsing the information for this movie on this site (BOM) was successful
BOMdf['title_bom'] = ''
BOMdf['reldate_bom'] = ''
BOMdf['dtg2016a'] = 0
BOMdf['genres'] = ''
BOMdf['runtime_bom'] = 0
BOMdf['mpaarating'] = ''
BOMdf['opwknd'] = ''
BOMdf['widestrel'] = 0
BOMdf['directors'] = ''

# Let's start with movie 0
movie_i = 0


# We'll try going through the first 100 or so movies, and see if we can parse all the info

i = 0

while i < len(BOMdf):

    soup = BeautifulSoup(BOMdf['soup_bom'][i])
    
    ### Title ###
    title_bom = soup.find('table',{'border':'0'}).find_all('td', {'valign':'top'})[2].contents[1].text
    #print(title_bom)
    #df.set_value(row, column, newValue)
    BOMdf.set_value(i, 'title_bom', title_bom)

    ### Release Date ###
    
    reldate_bom = soup.find(text=re.compile('Release Date')).findNextSibling().text
    reldate_bom = datetime.datetime.strptime(reldate_bom, '%B %d, %Y')
    BOMdf.set_value(i, 'reldate_bom', reldate_bom)
    
    ### Domestic Total Gross 2016 adjusted ###
    
    dtg2016a = soup.find(text=re.compile('Domestic Total Adj')).findNextSibling().text
    dtg2016a = float(re.sub('[$,]','',dtg2016a))
    BOMdf.set_value(i, 'dtg2016a', dtg2016a)
    
    ### Genres ###
    
    genres = soup.find(text=re.compile('Genre:')).findNextSibling().text
    BOMdf.set_value(i, 'genres', genres)
    
    ### Runtime from BOM ###
    
    runtime_bom = soup.find(text=re.compile('Runtime')).findNextSibling().text
    try:
        runtime_bom = datetime.datetime.strptime(runtime_bom, '%H hrs. %M min.')
    except ValueError:
        print('IndexError with:', i, title_bom, 'runtime_bom')
        runtime_bom = datetime.datetime.strptime('0 0','%H %M')
    hours = runtime_bom.time().hour
    minutes = runtime_bom.time().minute
    runtime_bom = minutes + (60*hours)
    BOMdf.set_value(i, 'runtime_bom', runtime_bom)
    
    ### MPAA Rating ###
    
    mpaarating = soup.find(text=re.compile('MPAA Rating')).findNextSibling().text
    BOMdf.set_value(i, 'mpaarating', mpaarating)
    
    ### Opening Weekend ###

    # Mini Soup for scraping Opening Weekend $ and Widest Release from BOM
    soup_2 = BeautifulSoup(str(soup.find_all(class_ = 'mp_box_content')[1]))

    if soup_2.find('a', href=re.compile('/weekend/chart/')) != None:
        opwknd = soup_2.find('a', href=re.compile('/weekend/chart/')).parent.findNextSibling().text
    else:
        # The movies with limited theatre openings seem to give this issue
        # So we make a new soup...
        testurl = BOMdf['url_bom'][i][:-22]
        response_test = requests.get(testurl)
        response_code_test = response_test.status_code
        if response_test.status_code > 399:
            print('Error with test access:', response_test.status_code)
        page = response_test.text
        test_soup = BeautifulSoup(page)

        test_soup = BeautifulSoup(str(test_soup.find_all(class_ = 'mp_box_content')[1]))
        #print(title_bom)
        if len(test_soup.find_all('a', href=re.compile('/weekend/chart/'))) > 1:
            opwknd = test_soup.find_all('a', href=re.compile('/weekend/chart/'))[1].parent.findNextSibling().text
        else:
            if len(test_soup.find_all('a', href=re.compile('/weekend/chart/'))) < 1:
                opwknd = '00000000'
            else:
                print('We\'re at:', i)
                opwknd = test_soup.find_all('a', href=re.compile('/weekend/chart/'))[0].parent.findNextSibling().text
#         try:
#             opwknd = test_soup.find_all('a', href=re.compile('/weekend/chart/'))[1].parent.findNextSibling().text
#         except IndexError:
#             print('IndexError with:', title_bom)
#             opwknd = -1
    
    try:
        opwknd = float(re.sub('[,]','',opwknd[2:]))
    except:
        print('Error for:', i, title_bom, 'opwknd')
        opwknd = -1.0
    BOMdf.set_value(i, 'opwknd', opwknd)
        
#     opwknd = float(re.sub('[,]','',opwknd[2:]))
#     BOMdf.set_value(i, 'opwknd', opwknd)
    
    ### Widest Release ###
    
    if soup_2.find(text=re.compile('Widest')) != None:
        widestrel = soup_2.find(text=re.compile('Widest')).parent.findNextSibling().text
        widestrel = int(re.sub('[theatres, ]','',widestrel[1:]))
    else:
        widestrel = 0
    BOMdf.set_value(i, 'widestrel', widestrel)
    
    ### Directors ###
    
    try:
        directors_obj = soup.find_all(class_='mp_box_content')[2].contents[1].contents[1]
    except IndexError:
        print('IndexError with:', i, title_bom, 'directors')
        directors_obj = ['unlisted']
    directors = []
    for child in directors_obj:
        try:
            directors.append(child.text)
        except AttributeError:
            print('AttributeError for:', i, title_bom, 'directors')
            directors = ['unlisted']
    # Gets rid of the first object which should always just be "Directors: "  
    directors.pop(0)
    try:
        BOMdf.set_value(i, 'directors', directors[0])
    except IndexError:
        BOMdf.set_value(i, 'directors', 'unlisted')
    
    
    ### ? ###
    
    i += 1
    #movie_i += 1


# Let's write this to a second csv

BOMdf.to_csv('03-BOMdone.csv')