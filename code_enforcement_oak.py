# -*- coding: utf-8 -*-
"""
Created on Thu Jul  1 10:13:13 2021

@author: sophi
"""

# IMPORT LIBS #
import pandas as pd
import datetime as dt
pd.options.mode.chained_assignment = None

# HELPER FUNCTIONS #
# input - specific violation and dict, output its type
def get_type(word, d):
    label = ""
    for x in list(d.items()):
        if word in x[1]:
            label = x[0]
    return(label)

# IMPORT DATA AND START #

df = pd.read_csv("C:/Users/sophi/Documents/OPDC/311_violations.csv")
df = df[df["NEIGHBORHOOD"].notnull()]

# get our neighborhoods of interest (contain "Oakland")
x = list(df["NEIGHBORHOOD"])
oaks = list(set([o for o in x if "Oakland" in o]))

oaks_df = df[df["NEIGHBORHOOD"].isin(oaks)]

# get REQUEST_TYPE of interest
# from code enforcement site: 
    # weeds/debris on property, abandoned vehicles on private property,
    # sidewalks that are a tripping hazard, electrical violations,
    # building violations, zoning violations
    
# k = list(set(oaks_df["REQUEST_TYPE"]))

# make dictionary of violation type: list of violations
vios_dict = {}

keys = ["Accessibility", 
        "Dumping",
        "Graffiti",
        "Occupancy",
        "Property Maintenance",
        "Sidewalk",
        "Signs",
        "Stormwater",
        "Street",
        "Trees",
        "Unpermitted Work",
        "Utility",
        "Vacant Property",
        "Vehicles",
        "Zoning"]

vals = [["Accessibility Construction Issue", 'Blocked or Closed Sidewalks', 
         'Business Accessibility'],
        ['Dumping, Private Property', 'Dumpster (on Street)', 'Dumpster'],
        ['Graffiti'],
        ['Overcrowding', 'Couch on Porch'],
        ['Retaining Wall Maintenance', 'Construction Site Maintenance', 
         'Building Maintenance', 'Sidewalk/Curb/HC Ramp Maintenance', 
         'Trail Maintenance','Fence Maintenance', 
         'Fire Safety System Issue', 'Fire Safety System Not Working', 
         'HVAC Not Functioning', 'Electrical Violation', "Weed/Debris", 'Wires'],
        ['Sidewalk has Ice or Litter', 'Broken Sidewalk', 
         'Sidewalk Obstruction', 'Curb Cuts', 'Manhole Cover ', 
         'Sidewalk/Curb/ADA Ramp Maintenance'],
        ['Sign', 'Signs, Advertising or Political'],
        ['Stormwater Runoff','Grate, Stormwater'],
        ["Road", 'Street Obstruction/Closure'],
        ['Tree Issues'],
        ['Building Without a Permit','Improper Work in a Historic District', 
         'Unpermitted Electrical Work', 'Unpermitted Land Operations', 
         'Unpermitted HVAC Work','Unpermitted Sign Construction', 
         'Unpermitted Fire System Work', 'Operating Without a License'],
        ['Utility Pole', 'Utility Cut - Other'],
        ['Vacant Building', 'Vacant Lot'],
        ["Abandoned Vehicle", 'Junk Vehicles'],
        ['Zoning Issue']]

# make vioation type dictionary, vios_dict
for i in range(len(keys)):
    vios_dict[keys[i]] = vals[i] 

# only include rows that include a relevant violation
all_vios = [vio for sub in vals for vio in sub]
df = oaks_df[oaks_df["REQUEST_TYPE"].isin(all_vios)]

# add column of violation type
df["VIO_TYPE"] = df["REQUEST_TYPE"].apply(lambda x: get_type(x, vios_dict)).to_frame()

# STATUS - 0 = New and 3 = Open, we want those
df = df[df["STATUS"].isin([0, 3])]

# change created on to a better date format for tableau
df["DATE"] = pd.to_datetime(df["CREATED_ON"]).dt.strftime("%m/%d/%Y")

# drop irrelevant columns
df = df.drop(["CREATED_ON", "GEO_ACCURACY"], axis = 1)

# now we can move to tableau and map
#df.to_csv("C:/Users/sophi/Documents/OPDC/oakland_enforcements.csv")

## get most occurring residences (problem residences) #

df["RES_COUNTS"] = df.groupby(["X", "Y"])["REQUEST_ID"].transform("count")
top = df.sort_values(by = ["RES_COUNTS"], ascending = False)[:25]

#top.to_csv("C:/Users/sophi/Documents/OPDC/top_res.csv")



