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
The following features are the variables that were scrapped, but not necessarily all that was engineered:  

##### Numerical:  
  * Domestic total gross adjusted to 2016  
  * Movie runtime  
  * MPAA rating (converted to an ordinal numerical value)  
  * Opening weekend value  
  * Widest release (number of theaters showing movie at point widest release)
  * Production budget  
  * Rotten Tomato Critic Rating  
  * Rotten Tomato User Rating  
  * Year released  
  * Month released  
  
##### Categorical (created through get_dummies() pandas call):  
  * Genre  
  * Director  

### Target Variable
Total video sales (dvd + bluray sales), after an 8 week period

### Data Sets
Training/test set - 1505 movies from 2006 to 2015  
Hold out set - 91 movies from 2016  

### Modeling/Results

#### Linear Regression / Baseline  

To create a sort of baseline to compare the other models to, I build a linear regression 'out of the box' model that included all the features listed above and no engineered features. From a 70/30 train/test split from the train/test data set and using root-mean-square error as a metric, we get:  
```
RMSE = 2.1805e7
```  
As a reminder: in general, we want to minimize this number to get an improved model. Let's now take a look at how our predictions look like compared to the actual values, graphically.  

![alt text](https://raw.githubusercontent.com/giancarlo-garbagnati/homevideosalepredictor/master/images/LR1-test.png "Predictions vs Actual (Test set)")  

This is a scatterplot graph of our predictions (on the x-axis) against the actual values (on the y-axis) for home video sales for the train/test set. Each blue dot represents one movie in the dataset, where its position on the y-axis represents the actual home video sale value and its position on the x-axis represents the model's prediction. The red line is simply just a one-to-one line, where if we had a perfect prediction model the blue dots would line up on exactly on. From this, we can see that our model doesn't look too bad right now, though we tend to be erring more often on overpredicting the home video sale values. Now, let's look at how well this model does on 2016 movies (the holdout set):

![alt text](https://raw.githubusercontent.com/giancarlo-garbagnati/homevideosalepredictor/master/images/LR1-holdout.png "Predictions vs Actual (Holdout set)")  

Here we can see our predicted values are quite off. However, what we also can see from this scatterplot (as well as from others not included), there's a bit of an exponential curve. This could be a scaling issue (ie. building a model using really large budget numbers alongside really small rating numbers can cause this).

#### Linear Regression, redux  

So assuming this is the case, one thing we can do is to transform the target values (home video sales numbers, the 'y'/target model values). So I redid the baseline model with this new transformed target values. Additionally, with this transformation, we can't simply use RSME anymore; we have to use 10^RMSE, which gives us:  
```
10^RMSE = 2.38
```  
This isn't as interpretive as just RMSE by itself, but it can still work as a metric to compare models against each other. Just as RMSE by itself, we want to minimize this as we try to build improved models.  

Let's look at our scatterplots now:  

Predictions vs Actual (Test Set):  
![alt text](https://raw.githubusercontent.com/giancarlo-garbagnati/homevideosalepredictor/master/images/LR1-test-tformed.png "Predictions vs Actual (Test set) - updated")  

Predictions vs Actual (Holdout Set):  
![alt text](https://raw.githubusercontent.com/giancarlo-garbagnati/homevideosalepredictor/master/images/LR1-holdout-tformed.png "Predictions vs Actual (Holdout set) - updated")  

These are a better than before, though it's still looking like we're overpredicting on the holdout set for some of the underperforming 2016 movies.  

Next, I tried two more tree-based models: random forest and gradient boosting.  

#### Random Forest  

With these more advanced models, there are more hyperparameters (tuning knobs, if you will) than linear regression. However, we'll start with an 'out-of-the-box' random forest model (RF1), using the default hyperparameter values from the scikit-learn implementation of random forest. This is performed on a 70/30 train/test split.
```
10^RMSE = 2.0579
```  
We'll compare this with two other random forest models that I tinkered with. RF2 uses 1000 estimators ('trees') and a min_samples_leaf of 5 (minimum number of samples on a estimator leaf node before you stop splitting on that node). Also performed on a 70/30 split.
```
10^RMSE = 1.9822
```
RF3 used GridSearch and cross-validation to determine hyperparameter values of 3000 estimators, a min_samples_leaf of 9, and a min_samples_split of 2 (min number of samples required to split in an internal node). This performs relatively as well as the above.
```
10^RMSE = 1.9887
```
The scatterplots for RF2 look like:
Predictions vs Actual (Test Set):  
![alt text](https://raw.githubusercontent.com/giancarlo-garbagnati/homevideosalepredictor/master/images/RF2-test.png "RF2-Predictions vs Actual (Test set)")  

Predictions vs Actual (Holdout Set):  
![alt text](https://raw.githubusercontent.com/giancarlo-garbagnati/homevideosalepredictor/master/images/RF2-holdout.png "RF2-Predictions vs Actual (Holdout set)")  

From both 10^RMSE and visually looking at the scatterplots, we can see that we've already improved on the linear regression model. I'll now move on to my gradient boosting models.  

#### Gradient Boosting  

Finally, I tried some gradient boosting models. The out-of-the-box gradient boosting model (GB1) from scikit-learn gets us:
```
10^RMSE = 1.9921
```
with a 70/30 split. This is better than the random forest out-of-the-box, but this isn't our best result. Since gradient boosting models are also based off of decision trees, we have a lot of the same hyper parameters as random forest. Thus, the next model I tried used the same hyper parameters used in the grid searched random forest model (above), in addition to a learning rate (alpha) of 0.1 and each boosting stage (n_estimator) used a subsample of 0.8. The loss function for this (and all the gradient boosting models used here) is the default one of least squared regression.
```
10^RMSE = 2.0867
```
So I went through a few more iterations of hyper parameter tweaking. Additionally, I removed some of the variables (all the directors). This model iteration (GB7):  
```python
gbmodel7 = GradientBoostingRegressor(subsample = 0.9, n_estimators = 3000, random_state = 1000, 
                                     learning_rate = 0.001, min_samples_leaf = 16, max_depth=5)
```  
performed the best of the gradient boosting models I tried.
```
10^RMSE = 1.9629
```  
Here are the scatterplots for GB7:
Predictions vs Actual (Test Set):  
![alt text](https://raw.githubusercontent.com/giancarlo-garbagnati/homevideosalepredictor/master/images/GB7-test.png "GB7-Predictions vs Actual (Test set)")  

Predictions vs Actual (Holdout Set):  
![alt text](https://raw.githubusercontent.com/giancarlo-garbagnati/homevideosalepredictor/master/images/GB7-holdout.png "GB7-Predictions vs Actual (Holdout set)")  

#### Feature Importances  

Most times it's just as (if not more) important to know how much each variable affects the final result than the prediction itself. That's where feature importances comes into. Here're the top feature importances from the GB7 model (described above):  

|Feature        |Importance|
|:-------------:|:--------:|
|dtg2016a       |0.420063  |
|reldate        |0.194056  |
|opwknd         |0.091252  |
|rt_user        |0.059876  |
|prodbud        |0.058187  |
|open_over_total|0.032693  |
|runtime        |0.030375  |
|rt_critic      |0.026028  |
|month          |0.016677  |
|mpaarating     |0.016345  |

To get successful home video sales, it looks like the gross domestic box office totals is by far the most meaningful variable. Release date (month and year) seems to be important as well. Next, we have opening weekend box office numbers. The rotten tomatoes user rating numbers is next, and is more than double the importance of the rotten tomatoes critic rating (down at 8th most important feature). Following that, we have a variable that represents a ratio of opening weekend sales over the total box office sales. Next, we have runtime, and as mentioned rotten tomatoes critic rating. Looking at the importance numbers though, only the first five seem to have more than a 0.05 importance, and only the top two (dtg2016a and reldate) have more than 0.1 importance.  

These numbers were generated through a call to a model variable, ```feature_importances_```.  

However, here's a caveat regarding these feature importance numbers. According to this model, the gross domestic total is the most meaningful variable, which makes intuitive sense. Also, we can likely make an intuitive guess as to the directionality of this variable (though we don't know for certain from these numbers!); likely more box office sales means more home video sales. However, how does theatrical release date (the next most important feature) affect home video sales? We don't have an intuitive answer for this, nor does the feature importances tell us this.  

So while random forest/gradient boosting models are typically much more accurate at predicting something like home video sales of movies, a simple linear regression model still has value when it comes to model/variable interpretability. Linear regression models will give coefficients for each variable, and the coefficient should give the directionality and magnitude of importance of each feature (whereas as we just demonstrated, the other two models really only gives magnitude). We'll address this more later however.  

#### Actionable model

Now, let's make this model more actionable. What do I mean by this? The models described above uses variables that you would only get after the movie was shot, editted, and released in the theatre. At that point, a movie production company wouldn't have much influence on the video sales, and the models made above can only serve to predict based on events that have already occured.  

Let's say we want to build a more actionable model. One in which we can use to try to optimize which variables to spend resources on to maximize home video sales. In short, this means removing a lot of the base variables we used above: domestic total gross (which was the most important feature in our model above) and opening weekend box office totals. (In hindsight, I should have also removed the rotten tomato scores as well, but the following models included that data).  

So a few gradient boosting model iterations later and we have GB11 and GB13:  

```python
#GB11
gbmodel11 = GradientBoostingRegressor(subsample = 0.9, n_estimators = 3000, random_state = 1000, 
                                     learning_rate = 0.001, min_samples_leaf = 16, max_depth=5)
```  
```
10^RMSE = 2.5013
```  

```python
#GB13
gbmodel13 = GradientBoostingRegressor(random_state=1000, n_estimators=100, min_samples_split=5, min_samples_leaf=2,
                                      max_features = 3, subsample=1.0, learning_rate=0.005, max_depth =3)
```  
```
10^RMSE = 3.2501
```  


