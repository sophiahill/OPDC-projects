# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 10:16:26 2021

@author: sophi
"""

############################################################
# LIBRARIES
############################################################

import pandas as pd
from time import sleep
import re
import random

# selenium libs
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

############################################################
# HELPER FUNCTIONS
############################################################

def initialize_bot():
    chrome_options = Options()
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-backgrounding-occluded-windows')
    chrome_options.add_argument('--disable-background-timer-throttling')
    chrome_options.add_argument('--disable-renderer-backgrounding')
    chrome_options.add_argument('detach:True')
    chrome_options.add_argument('log-level=3')
    chrome_options.add_argument("--window-size=1080,760")
    chrome_options.add_argument('--headless') # run this line if you want pop up window
    return webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)

def sleep_for(opt1, opt2):
    time_for = random.uniform(opt1, opt2)
    time_for_int = int(round(time_for))
    sleep(abs(time_for_int - time_for))
    for i in range(time_for_int, 0, -1):
        sleep(1)
       
# give a list of addresses, returns a dataframe with 
# lat, lon column
def get_lat_lon(addresses):
    bot = initialize_bot()
    lats = []
    lons = []
    
    for a in addresses:
        loc_url = 'https://www.google.com/maps/search/' + \
            re.sub('[^a-zA-Z0-9 \n\.]', '',
                   a).replace('  ', ' ').replace(' ', '+')
        bot.get(loc_url)
        sleep_for(7, 9) # needs to be long enough so url loads
        
        url = bot.current_url
        print("Got url: ", url)
        urlstring = url.split('!3d')[1]
        lat = urlstring.split('!4d')[0]
        lon = urlstring.split('!4d')[1].split('?')[0]
        
        print(lat, lon)
        
        lats.append(lat)
        lons.append(lon)
        
        print("Added")
        print("\n")
        
    bot.quit()
        
    geo = pd.DataFrame([lats, lons])
    geo = geo.transpose()
    geo.columns = ["Lat", "Lon"]
    
    return(geo)

trees = pd.read_csv("C:/Users/sophi/Documents/OPDC/trees/potential_trees.csv",
                    encoding = "unicode_escape")

# Add "Pittsburgh, PA" to addresses
trees["Address"] = trees["Address"] + ", Pittsburgh, PA"

# Use selenium to get lat, lon from gmaps urls
    # combine returned df side-by-side
geo = get_lat_lon(trees["Address"])
new_trees = pd.concat([trees, geo], axis = 1)

new_trees.to_csv("pot_locs.csv")
print("Everything's done - check pot_locs.csv")

# MERGING DFS
existing = pd.read_csv("C:/Users/sophi/Documents/OPDC/trees/annalise_current_trees.csv")
potential = pd.read_csv("C:/Users/sophi/Documents/OPDC/trees/annalise_potential_trees.csv")

comb = pd.concat([existing, potential], axis = 0, ignore_index = True)

# drop "Unnamed: 7"
comb = comb.drop(["Unnamed: 7"], axis = 1)

# combine Note cols
comb = comb.fillna("")
comb["Note"] = comb["Note"] + comb["Note.1"]
comb = comb.drop(["Note.1"], axis = 1)

comb.to_csv("trees_final.csv", index = False)
