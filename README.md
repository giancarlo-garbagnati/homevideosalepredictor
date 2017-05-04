# homevideosalepredictor
Predicting home video sales using regression models  
Project Date: Feb 2017

## Description

Using movie data (production data, box office data, etc), I was curious to see how effective regression models would be in trying to predict the home video (dvd/bluray) sales for movies. This project was done while I was enrolled in the Metis Data Science Bootcamp Program in SF (winter 2017), and some of the requirements was use some kind of web scraping tool with python, and that APIs could not be used for this project.

## Data Acquisition

All of the data for this project was sourced through web scraping through three websites (box office mojo, the-numbers, and rotten tomatoes) using the python package, BeautifulSoup. 

The general scraping strategy was to scrap from one website (box office mojo, in this case), then use the movie title to locate the same movie on the other websites. Other identifying information scraped from the first website was used to corroborate that we were looking at the correct movie from the other movies.

The top 200 movies from each year from 2006 to 2015 (+ 2016) was scraped from box office mojo, and then those same movies' data was scraped from the-numbers and rotten tomatoes as mentioned above. Movies were only included in the final data set if all variables was able to be sourced through the three websites. As alluded to, data from 2016 was collected, but not to be used for the training sets, and instead for the final holdout set test.

## Dataset

### Variables  
Numerical:  
  * Domestic total gross adjusted to 2016  
  * Movie runtime  
  * MPAA rating (converted to an ordinal numerical value)  
  * Opening weekend value  
  * Production budget  
  * Rotten Tomato Critic Rating  
  * Rotten Tomato User Rating  
  * Year released  
  * Month released  
  
Categorical (created through get_dummies() pandas call):  
  * Genre  
  * Director  

### Target Variable
Total video sales (dvd + bluray sales), after an 8 week period

### Data Sets
Training/test set - movies from the 10 year period of 2006 to 2015 (1505 total movies)  
Hold out set - 91 movies from 2016  
