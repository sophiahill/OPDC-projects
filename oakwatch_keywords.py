# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 15:47:18 2021

@author: sophi
"""
#%%
# import libs
import pandas as pd
import yake
from tika import parser
import re
import numpy as np

#%%
# get text from pdfs
def get_text(path):
    raw = parser.from_file(path)
    text = str(raw['content'])
    text = text.strip()
    return text

# clean text of words we don't want to be keywords, including names
def clean_text(text):
    to_replace = [r"Oakland", r"City", r"Zone", r"Pittsburgh",
                  r"n't", r"Maria", r"Andrea", r"January",
                  r"February", r"March", r"May", r"Boykowycz",
                  r"Liz", r"Gray", r"Adam", r"Elena", r"Camille",
                  r"Minutes", r"Dixon", r"Catherine", r"Zaitsoff",
                  r"Rodriguez", r"Danielle", r"ASloan", r"Officer",
                  r"John", r"Daniel", r"iPhone"]
    for word in to_replace:
        text = re.sub(word, "", text, flags = re.S)
        
    return(text)

# get keywords from cleaned text
def get_keywords(text):
    language = "en"
    max_ngram_size = 1
    num = 50
    
    kw_extractor = yake.KeywordExtractor(lan = language, n = max_ngram_size, top = num)
    keywords = kw_extractor.extract_keywords(text)
    
    words_list = []
    for kw in keywords:
        words_list.append(kw[0])

    return(words_list)

#%%
month_list = ["jan", "feb", "march", "may"]
months_df = pd.DataFrame(columns = month_list)

i = -1
for month in month_list:
    i += 1
    file = "C:/Users/sophi/Documents/OPDC/" + month + "_minutes.pdf"
    text = get_text(file) 
    cleaned = clean_text(text)
    keywords = np.asarray(get_keywords(cleaned))
    months_df[month] = keywords
    
#%%
# save to csv
months_df.to_csv("C:/Users/sophi/Documents/OPDC/opdc_words.csv")
    
    
#%%
