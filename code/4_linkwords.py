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


def summarise_linkwords(app_name, df):
    # get dataframe for app_name
    dff = df[df['app_name']==app_name]
    
    # compute count and mean for every link word
    dff = dff.groupby('link_words')['rating']\
             .agg(['count','mean'])\
             .sort_values(by=['count','mean'], ascending=[False,False])\
             .reset_index()
    dff = dff.rename(columns={'mean':'rating'})
    dff['rating'] = dff['rating'].round(2)

    # determine sentiment based on rating
    conditions = [(dff['rating'] > 3.5),
                  (dff['rating'] < 2.5),
                  (dff['rating'] >= 2.5) & (dff['rating'] <= 3.5)
                 ]
    values = ['Positive', 'Negative', 'Neutral']
    dff['sentiment'] = np.select(conditions, values)

    # save to csv
    dff.to_csv('data/linkwords/linkwords_summary_{}.csv'.format(app_name.lower()), index=False, encoding='utf8')


# rule 1: verb, noun(object)
def rule1(doc):
    
    link_words = []
    
    for token in doc:
        
        # if the token is a verb
        if (token.pos_=='VERB'):
            
            phrase = ''
            
            for right_tok in token.rights:
                
                if (right_tok.dep_ in ['dobj']) and (right_tok.pos_ in ['NOUN','PROPN']):
                    
                    phrase += token.text + ' ' + right_tok.text
                    link_words.append(phrase)

    return link_words


# rule 2: noun(subject), verb
def rule2(doc):
    
    link_words = []
    
    for token in doc:
        
        if (token.pos_=='VERB'):
            
            phrase =''
            
            for left_tok in token.lefts:
                
                # only extract noun or proper noun subjects
                if (left_tok.dep_ in ['nsubj','nsubjpass']) and (left_tok.pos_ in ['NOUN','PROPN']):
                
                    phrase += left_tok.text + ' ' + token.lemma_
                    link_words.append(phrase)
            
    return link_words


# rule 3: noun(subject), verb, noun(object)
def rule3(doc):
    
    link_words = []
    
    for token in doc:
        
        # if the token is a verb
        if (token.pos_=='VERB'):
            
            phrase = ''
            
            # only extract noun or pronoun subjects
            for left_tok in token.lefts:
                
                if (left_tok.dep_ in ['nsubj','nsubjpass']) and (left_tok.pos_ in ['NOUN','PROPN']):
                    
                    # add subject to the phrase
                    phrase += left_tok.text

                    # save the root of the verb in phrase
                    phrase += ' '+token.lemma_ 

                    # check for noun or pronoun direct objects
                    for right_tok in token.rights:
                        
                        if (right_tok.dep_ in ['dobj']) and (right_tok.pos_ in ['NOUN','PROPN']):
                                    
                            phrase += ' ' + right_tok.text
                            link_words.append(phrase)
            
    return link_words


# rule 4: noun(subject), Adj
def rule4(doc):

    link_words = []
    
    for token in doc:
        
        phrase = ''
        
        # if the word is a subject noun or an object noun
        if (token.pos_ == 'NOUN') and (token.dep_ in ['dobj','pobj','nsubj','nsubjpass']):
            
            for subtoken in token.children:
                
                # if word is an adjective or has a compound dependency
                if (subtoken.pos_ == 'ADJ') or (subtoken.dep_ == 'compound'):
                    phrase += subtoken.text + ' '
                    
            if len(phrase)!=0:
                phrase += token.text
             
        if len(phrase)!=0:
            link_words.append(phrase)
        
    return link_words


# rule 5: noun(subject), Noun
def rule5(doc):
    
    link_words = []
    
    for token in doc:

        # look for prepositions
        if token.pos_=='ADP':

            phrase = ''
            
            # if head word is a noun
            if token.head.pos_=='NOUN':
                
                # append noun and preposition to phrase
                phrase += token.head.text + ' ' + token.text

                # check the nodes to the right of the preposition
                for right_tok in token.rights:
                    
                    # append if it is a noun or proper noun
                    if (right_tok.pos_ in ['NOUN','PROPN']):
                        phrase += ' ' + right_tok.text
                
                if len(phrase)>2:
                    link_words.append(phrase)
                
    return link_words


if __name__ == '__main__':
    nlp = spacy.load('en_core_web_sm')
    os.makedirs('data/linkwords/', exist_ok=True)
    
    with open('data/apps.txt') as fileIn:
        apps = dict(line.strip().split(',') for line in fileIn)

    df = pd.read_csv('data/all_reviews.csv', encoding='utf8')
    
    df_link = pd.DataFrame()

    for index, row in enumerate(df['review']):
        doc = nlp(row)
        
        r1 = rule1(doc)
        r2 = rule2(doc)
        r3 = rule3(doc)
        r4 = rule4(doc)
        r5 = rule5(doc)
        
        overall_lw = r1 + r2 + r3 + r4 + r5
        
        df_row = df.iloc[index].to_frame().T
        df_row_replicated = pd.DataFrame(np.repeat(df_row.values, len(overall_lw), axis=0), columns=df.columns)
        df_row_replicated['link_words'] = overall_lw
        df_link = pd.concat([df_link, df_row_replicated])

    df_link['rating'] = df_link['rating'].astype(str).astype(int)
    
    for app_name in apps.keys():
        dff = df_link[df_link['app_name']==app_name].reset_index(drop=True)
        dff.to_csv('data/linkwords_table_{}.csv'.format(app_name.lower()), index=False, encoding='utf8')

    inputs = zip(apps.keys(), repeat(df_link))
    with Pool(cpu_count()) as pool:
        result = list(pool.starmap(summarise_linkwords, inputs))