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


def combine_data(app_names):        
    dff = pd.concat(pd.read_csv('data/app_reviews/reviews_{}.csv'.format(app_name.lower()), encoding='utf8') \
                             for app_name in app_names)
    
    dff = dff.sort_values(['app_name','date'], ascending=[True, False])
    
    return dff.reset_index(drop=True)

def clean_data(df):
    # rename columns
    df = df.rename(columns={'stars':'rating', 'text':'review'})
    
    # determine sentiment
    conditions = [(df['rating'] > 3),
                  (df['rating'] < 3),
                  (df['rating'] == 3)
                 ]
    values = ['Positive', 'Negative', 'Neutral']
    df['sentiment'] = np.select(conditions, values)
    
    # determine day
    df['day'] = df['date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').strftime('%A'))
    
    # determine app version levels
    def versioning(version):
        ver_lvls = version.split('.')
        levels = len(ver_lvls)
        
        if levels == 1:
            return ver_lvls[0] + '.0.0.0'
        elif levels == 2:
            return ver_lvls[0] + '.' + ver_lvls[1] + '.0.0'
        elif levels == 3:
            return version
        
    df['version'] = df['version'].apply(versioning)
    
    df['version_lvl1'] = df['version'].apply(lambda x: x.split('.')[0])
    df['version_lvl2'] = df['version'].apply(lambda x: x.split('.')[0] + '.' + x.split('.')[1])
    df['version_lvl3'] = df['version'].apply(lambda x: x.split('.')[0] + '.' + x.split('.')[1] + '.' + x.split('.')[2])
    
    df = df.drop(columns=['version'])
    
    # rearrange columns
    df = df[['title', 'review', 'username',
             'app_name', 'app_id', 'country',
             'rating', 'sentiment',
             'date', 'day',
             'version_lvl1', 'version_lvl2', 'version_lvl3']]
                                              
    return df.reset_index(drop=True)

if __name__ == '__main__':
    with open('apps.txt') as fileIn:
        apps = dict(line.strip().split(',') for line in fileIn)
    
    os.makedirs('data/app_reviews/', exist_ok=True)
    
    df = combine_data(apps.keys())
    df = clean_data(df)
    df.to_csv('data/all_reviews.csv', encoding='utf8', index=False)