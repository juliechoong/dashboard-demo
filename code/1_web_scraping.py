from datetime import datetime
from itertools import repeat
from multiprocessing import Pool, cpu_count
import numpy as np
import os
import pandas as pd
import re
import spacy
import string

from bertopic import BERTopic
from itunes_app_review_scraper import iTunesScraper
import emoji

def scrape_app(app_name, app_id):
    reviews = iTunesScraper.get_reviews(app_id=app_id, country='MY')
    dff = pd.DataFrame(reviews)
    
    dff['app_id'] = app_id
    dff['app_name'] = app_name
    dff['country'] = 'Malaysia'

    filename = 'data/app_reviews/reviews_{}.csv'.format(app_name.lower())
    dff.to_csv(filename, index=False, encoding='utf8')

if __name__ == '__main__':
    with open('data/apps.txt') as fileIn:
        apps = dict(line.strip().split(',') for line in fileIn)

    inputs = zip(apps.keys(), apps.values())
    with Pool(cpu_count()) as pool:
        pool.starmap(scrape_app, inputs)