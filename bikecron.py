#!/usr/bin/python3

import requests
import json
import numpy as np
import pandas as pd
from datetime import datetime

#get feed links
url = 'http://gbfs.citibikenyc.com/gbfs/gbfs.json'
response = requests.get(url)

#create dictionary of links
citibike_feed = json.loads(response.text)['data']['en']['feeds']
feed_dict = {i['name']:i['url'] for i in citibike_feed}
feed_dict['bike_angels'] = 'https://layer.bicyclesharing.net/map/v1/nyc/stations'
feed_dict

#get JSONs from links
station_information = json.loads(requests.get(feed_dict['station_information']).text)['data']['stations']
station_status = json.loads(requests.get(feed_dict['station_status']).text)['data']['stations']
angels = json.loads(requests.get(feed_dict['bike_angels']).text)['features']

#create dataframes
status_df = pd.DataFrame(station_status)
stations_df = pd.DataFrame(station_information)

angels_df = pd.DataFrame([i['properties'] for i in angels])
angels_df = angels_df[['station_id','bike_angels_action', 'bike_angels_points',
       'bike_angels_digits']]

#combine dataframes and some cleaning
df = pd.merge(stations_df,status_df,on='station_id')
df = pd.merge(df,angels_df,on='station_id')

conditions = [
    df.bike_angels_action.isna() == True,
    df.bike_angels_action == 'neutral',
    df.bike_angels_action == 'give',
    df.bike_angels_action == 'take',
]

choices = [0,0,df.bike_angels_points,df.bike_angels_points*(-1)]

df.bike_angels_points = np.select(conditions,choices,df.bike_angels_points)

#save to csv
path = '~/Desktop/live_data/bike_data_' + datetime.now().strftime('%m-%d-%y_%H-%M') + '.csv'
df.to_csv(path)