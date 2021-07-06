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


def calculate_topics(input_file):
    def get_keywords(id):
        return '_'.join([topic[0] for topic in model.get_topic(id)][:5])
                    
    # Get reviews
    df = pd.read_csv(input_file)
    corpus = list(df['review'].astype(str))
    
    print('Calculating the topics for {} sentences. This might take a while.'.format(len(corpus)))
    model = BERTopic(embedding_model='paraphrase-TinyBERT-L6-v2', nr_topics='auto')
    topics, _ = model.fit_transform(corpus)
    
    df['topic_id'] = topics
    df['topic_keywords'] = [get_keywords(id) for id in df['topic_id']]
    
    df.to_csv('data/all_reviews_topics.csv', index=False, encoding='utf8')
    
    return df


def summarise_topics(app_name, df):
    # get dataframe for app_name
    df = df[df['app_name']==app_name]

    # compute count for every topic
    df = df.groupby(by=['topic_id','topic_keywords']).size()\
           .sort_values(ascending=False)\
           .reset_index(name='count')

    filename = 'data/topics/topics_{}.csv'.format(app_name.lower())
    df.to_csv(filename, index=False, encoding='utf8')


if __name__ == '__main__':
    with open('apps.txt') as fileIn:
        apps = dict(line.strip().split(',') for line in fileIn)

    os.makedirs('data/topics/', exist_ok=True)
    df_topics = calculate_topics('data/all_reviews.csv')
    
    inputs = zip(apps.keys(), repeat(df_topics))
    with Pool(cpu_count()) as pool:
        list(pool.starmap(summarise_topics, inputs))