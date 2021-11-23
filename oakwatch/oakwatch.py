# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 13:42:34 2021

@author: sophi
"""
#%%
# IMPORT LIBS #
# use tika to extract text from PDF
from tika import parser
import pandas as pd
import re
import string
import functools
import matplotlib.pyplot as plt
from collections import Counter
#%%
# INITIALIZE THINGS TO ITERATE OVER #
crime_sections = ["Pittsburgh Police Zone 4 Police",
            "University of Pittsburgh Police"]
#%%
# PDF TO MULTI-LINE STRING #
def get_text(path):
    raw = parser.from_file(path)
    text = str(raw['content'])
    text = text.strip()
    return text
#%%
# TO DF FUNC #
def list_to_df(matches):
    dic = {"Name": [], "Number": []}
    crimes = pd.DataFrame(dic)
    for crime in matches:
        to_add = {"Name": crime[0], "Number": crime[1]}
        crimes = crimes.append(to_add, ignore_index = True)
    return(crimes)

# getting to list based on colon / no colon
def c_nc_split(match_list):
    # split between either : and number (if : present)
        # or split between letter and number (if no :)
    colon = r": "
    no_colon = r"([a-zA-Z]) (\d)"
    
    # getting list of zone 4 section 1
    splited = []
    for crime in match_list:
        if crime == "" or crime == ": ": 
            continue
        if "Increase" in crime:
            crime = crime.replace("Increase from ", "")
        if "Decrease" in crime:
            crime = crime.replace("Decrease from ", "")
        if ":" in crime:
            x = re.split(colon, crime, maxsplit = 1)
        else:
            y = re.split(no_colon, crime, maxsplit = 1)
            x = [y[0] + y[1], y[2] + y[3]]
            
        # if a list
        if isinstance(x, list):
            x = [phrase.strip() for phrase in x]
        else:
            x = list(x)
        
        x = [word.strip() for word in x]
        if x == "":
            continue
        splited.append(x)
        
    return splited

# string "num to num" to range - takes series col
def str_to_nums(x):
    if "to" not in x:
        return(x)
    x = x.replace(" to ", " ")
    return(x)
#%%
# ZONE SECTION #
def zone_4_police(text):
    # get text between "Pittsburgh Police Zone 4 Police" and "Arrests"
    zone_text = re.search(r"Pittsburgh Police Zone 4 Police(.*?)Arrests", text, flags = re.S)
    zone_match = zone_text.group(1).strip().splitlines()
    
    # get text between "Arrests" and "Total Arrests"
    zone_arrests = re.search(r"Arrests(.*?)Total Arrests: \w", text, flags = re.S)
    arrests_match = zone_arrests.group(1).strip().splitlines()
    
    # get only the relevant lines
    zone_match = [line for line in zone_match if "to" in line]
    for zone in zone_match:
        if "Crime Stats" in zone:
            zone_match.remove(zone)
    
    # from string to list of [crime name, amount]
    zone_split = c_nc_split(zone_match)
    arrests_split = c_nc_split(arrests_match)
    
    # MAKE INTO CRIMES, ARRESTS DFs #
        # for crimes
    zone_df = list_to_df(zone_split)
    arrests_df = list_to_df(arrests_split) 
    
    to_add = {"Name": "Overall", "Number": str(arrests_df["Number"].astype(int).sum())}
    arrests_df = arrests_df.append(to_add, ignore_index = True)
    
    return (zone_df, arrests_df)

def word_count(text):
    words = text.lower()
    words = words.strip()
    words = re.sub("[^0-9a-zA-Z]+", " ", words)
    tokens = words.split(" ")
    counts = Counter(tokens)
    return(counts)

#%%
# GET ZONE 4 STATS FOR ALL MONTHS #
month_list = ["jan", "feb", "march", "may"]
month_dict = {}
cts_dict = {}

for month in month_list:
    file = "C:/Users/sophi/Documents/OPDC/" + month + "_minutes.pdf"
    text = get_text(file) 
    # get word counts in df
    cts = word_count(text)
    cts_dict[month] = cts
    # get crime stats
    #month_dict[month] = zone_4_police(text)
#%%
# combine crime stats dfs and arrests dfs for all months #
    # crime stats - months are cols, crimes are rows #
crime_stats = []
arrests = []
for m in month_list:
    crime_stats.append(month_dict[m][0])
    arrests.append(month_dict[m][1])
#%%
# created merged dfs for crime stats and arrests
crime_stats_df = functools.reduce(lambda left, right: pd.merge(left, right, on = ["Name"], how = "outer"),
                crime_stats).fillna("")
arrests_df = functools.reduce(lambda left, right: pd.merge(left, right, on = ["Name"], how = "outer"),
                arrests).fillna("")

c = ["crime"]
for m in month_list:
    c.append(m)
    
(crime_stats_df.columns, arrests_df.columns) = (c, c)
#%%
# put in order of alphabetical row names with Overall last
crime_stats_df = crime_stats_df.sort_values("crime")
arrests_df = arrests_df.sort_values("crime")

#%%
# change "to" in crime_stats_df to range of values
crime_stats_df.iloc[:, 1:] = crime_stats_df.iloc[:, 1:].apply(lambda x: x.apply(str_to_nums))
#%%
# do visualizations in tableau - save to csv
#crime_stats_df.to_csv("C:/Users/sophi/Documents/OPDC/crime_stats.csv")
#arrests_df.to_csv("C:/Users/sophi/Documents/OPDC/arrests.csv")

#%%
print(cts_dict["march"])
