# imports
from __future__ import print_function, division
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import datetime

import re # regular expressions
import requests


# To instantiate or reset the following lists
urlID = []
urlList = []
soupList = []


### BOM Year (2006-2015=data, 2016=test)
# Since we're running into problems along the way, let's do this year by year
currentYear = 2006
endYear = 2016
#currentYear = 2006
#endYear = 2016
#BOM_df = pd.dataframe()
curr_urlID = []
curr_urlList = []
curr_soupList = []

while currentYear < endYear+1:
#while currentYear < 2007:
    ### Setting the current year
    url_bom_year_start = 'http://www.boxofficemojo.com/yearly/chart/?page='
    url_bom_year_end = '&view=releasedate&view2=domestic&yr=' + str(currentYear) + '&p=.htm'
    
    # Let's get the number of movies in this year
    url_bom_year_start = 'http://www.boxofficemojo.com/yearly/chart/?page='
    url_bom_year_end = '&view=releasedate&view2=domestic&yr=' + str(currentYear) + '&p=.htm'

    url_bom_year = (url_bom_year_start + str(1) + url_bom_year_end)
    #print(url_bom_year)
    response_bom_year = requests.get(url_bom_year)
    response_code_bom_year = response_bom_year.status_code
    if response_bom_year.status_code > 399:
        print('Error with BOM-', currentYear, 'access:', response_bom_year.status_code)

    page = response_bom_year.text
    soup_bom_year = BeautifulSoup(page)

    movies_in_this_year = int(soup_bom_year.find(text=re.compile('Movies on Chart')).parent.text[11:14])
    # Yeah above's all fine and dandy, but for the sake of completing this project and for my sanity,
    #  I'm just going to pull 200/year
    movies_in_this_year = 200

    print(movies_in_this_year)
    ## We have the number of movies this year
    
    #moreMovies = True
    page_no = 1
    # i here is the index for the movie number for the current year
    i = 0
    
    #while moreMovies is True:
    while i < (movies_in_this_year):
        ### Setting the current page
        url_bom_year = (url_bom_year_start + str(page_no) + url_bom_year_end)
        print(url_bom_year)
        
        try:
            response_bom_year = requests.get(url_bom_year)
            response_code_bom_year = response_bom_year.status_code
            if response_bom_year.status_code > 399:
                print('Error with BOM-', currentYear, 'access:', response_bom_year.status_code)
            #print(response_code_bom_year)

            page = response_bom_year.text
            soup_bom_year = BeautifulSoup(page)
        except ConnectionResetError:
            print('ERROR: page=', page_no, url_bom_year)
            

        # Why are we ending up here?
        if currentYear == 2016 and page_no == 9:
            break
        
        ### Let's start scraping the page
        currentRow = soup_bom_year.find_all('tr', bgcolor='#ffffff')[0].findPreviousSibling()

        # Get the first row
#         this_url = currentRow.contents[1].find('a')['href'][12:-4]
#         urlList.append(this_url)

        # j here is the index for the page
        j = 0
        # To fix a single case in 2016, where one page has 101 entries instead of the usual 100
        if currentYear == 2016 and page_no == 7:
            j = -1
#         if currentYear == 2016 and page_no == 8:
#             j = 1
        
        while j < 101:
            currentRow = currentRow.findNextSibling()

            i += 1
            j += 1
            
            # Check to see if we're at the end of the chart
            if 'Movies on Chart:' in currentRow.text:
                break

                
            
            # Let's get and store this movie's url ID
            this_url_ID = currentRow.contents[1].find('a')['href'][12:-4]
            curr_urlID.append(this_url_ID)
            
            # Let's get and store this movie's url
            this_url_start = 'http://www.boxofficemojo.com/movies/?id='
            this_url_end = '.htm&adjust_yr=2016&p=.htm'
            this_url = this_url_start + this_url_ID + this_url_end
            curr_urlList.append(this_url)
            
            # Let's get and store this movie's soup
            response_this = requests.get(this_url)
            response_code_this = response_this.status_code
            if response_code_this > 399:
                print('Error with BOM-', currentYear, 'access:', response_code_this)
            page = response_this.text
            this_soup = BeautifulSoup(page)
            curr_soupList.append(this_soup)
            
            
        print(j)
        # Check if if i is not a multiple of 100, and if so switch to another year
        #if i % 100 != 0:
        #    print(i)
        #    moreMovies = False
        
        # Increment the page number
        page_no += 1
    
    
    currentYear += 1

# Adding current lists to overall lists
urlID = urlID + curr_urlID
urlList = urlList + curr_urlList
soupList = soupList + curr_soupList

# YEARS DONE: 2006-2015

# Sanity check
print( 'Sanity Check' )
print( len(urlID) == len(urlList) )
print( len(urlID) == len(soupList) )
print( len(urlID) )

BOMdf = pd.DataFrame()
BOMdf['urlID_bom'] = urlID
BOMdf['url_bom'] = urlList
BOMdf['soup_bom'] = soupList
BOMdf.head()

# Let's write this to a first csv

BOMdf.to_csv('02-BOMlinks_200per.csv')