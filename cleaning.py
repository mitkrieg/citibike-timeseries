import pandas as pd
import numpy as np
import requests
import json
import datetime as dt
import pickle


#retrieve data links from citibike
url = 'http://gbfs.citibikenyc.com/gbfs/gbfs.json'
response = requests.get(url)

#retrieve json from citibike and load relevant information
citibike_feed = json.loads(response.text)['data']['en']['feeds']
feed_dict = {i['name']:i['url'] for i in citibike_feed}
feed_dict['bike_angels'] = 'https://layer.bicyclesharing.net/map/v1/nyc/stations'

regions_raw = json.loads(requests.get(feed_dict['system_regions']).text)['data']['regions']
#reformat region
regions = {}
for region in regions_raw:
    regions[region['region_id']] = region['name']

def station_initalize():
    """
    Initalizes DataFrame of stations with most current information
    """
    #requests and reads json from CitiBike
    station_information = json.loads(requests.get(feed_dict['station_information']).text)['data']['stations']
    station_status = json.loads(requests.get(feed_dict['station_status']).text)['data']['stations']
    angels = json.loads(requests.get(feed_dict['bike_angels']).text)['features']
    
    #convert to dataframe
    status_df = pd.DataFrame(station_status)
    stations_df = pd.DataFrame(station_information)

    angels_df = pd.DataFrame([i['properties'] for i in angels])
    angels_df = angels_df[['station_id','bike_angels_action', 'bike_angels_points',
           'bike_angels_digits']]

    #join into one dataframe
    live_df = pd.merge(stations_df,status_df,on='station_id')
    live_df = pd.merge(live_df,angels_df,on='station_id')
    live_df.drop(labels=list(live_df.loc[live_df.station_status == 'out_of_service'].index), inplace=True)
    
    live_df.station_id = live_df.station_id.astype(int)

    #give direction to bike angle point valies
    conditions = [
        live_df.bike_angels_action.isna() == True,
        live_df.bike_angels_action == 'neutral',
        live_df.bike_angels_action == 'give',
        live_df.bike_angels_action == 'take',
    ]

    choices = [0,0,live_df.bike_angels_points,live_df.bike_angels_points*(-1)]

    live_df.bike_angels_points = np.select(conditions,choices,live_df.bike_angels_points)

    #rename name column
    live_df.rename(columns={'name':'station_name'},inplace=True)
    
    return live_df

def trip_initialize():
    """
    Reads Trip data and returns two time series by start station and end station
    *** Currently only 2018 ***
    """
    #read trips
    filepaths = ['./trip_data/201801-citibike-tripdata.csv',
                './trip_data/201802-citibike-tripdata.csv',
                './trip_data/201803-citibike-tripdata.csv',
                './trip_data/201804-citibike-tripdata.csv',
                './trip_data/201805-citibike-tripdata.csv',
                './trip_data/201806-citibike-tripdata.csv',
                './trip_data/201807-citibike-tripdata.csv',
                './trip_data/201808-citibike-tripdata.csv',
                './trip_data/201809-citibike-tripdata.csv',
                './trip_data/201810-citibike-tripdata.csv',
                './trip_data/201811-citibike-tripdata.csv',
                './trip_data/201812-citibike-tripdata.csv',]

    trip_dfs = [pd.read_csv(path) for path in filepaths]

    trips = pd.concat(trip_dfs)
    
    #rename columns
    cols = [col.replace(" ","_") for col in trips.columns]
    trips.columns = cols

    trips.dropna(inplace=True)

    #change times to datetime objects
    trips.starttime = pd.to_datetime(trips.starttime, format='%Y-%m-%d %H:%M:%S.%f')
    trips.stoptime = pd.to_datetime(trips.starttime, format='%Y-%m-%d %H:%M:%S.%f')
    
    #add day of week and weedday feature
    trips['day_of_week'] = trips.starttime.dt.weekday
    trips['weekday'] = np.where(trips.day_of_week<5,True,False)

    pickle_out = open('trips.pickle','wb')
    pickle.dump(trips, pickle_out)
    pickle_out.close()

    # multihierarchical index time series 
    ts_starts_df = trips.set_index(['start_station_id','starttime']).sort_values(['start_station_id','starttime'])
    ts_ends_df = trips.set_index(['end_station_id','stoptime']).sort_values(['end_station_id','stoptime'])

    return ts_starts_df, ts_ends_df

def historical_initalize():
    """
    Reads historical station data and returns a multiindex pandas time series 
    *** Currently only 2018
    """
    # read historical station data
    filepaths = ['./station_data/bikeshare_nyc_raw_jan2018.csv',
                './station_data/bikeshare_nyc_raw_feb2018.csv',
                './station_data/bikeshare_nyc_raw_mar2018.csv',
                './station_data/bikeshare_nyc_raw_apr2018.csv',
                './station_data/bikeshare_nyc_raw_may2018.csv',
                './station_data/bikeshare_nyc_raw_June_2018.csv',
                './station_data/bikeshare_nyc_raw_july2018.csv',
                './station_data/bikeshare_nyc_raw_Aug2018.csv',
                './station_data/bikeshare_nyc_raw_Sept2018.csv',
                './station_data/bikeshare_nyc_raw_oct2018.csv',
                './station_data/bikeshare_nyc_raw_Nov2018.csv',
                './station_data/bikeshare_nyc_raw_dec2018.csv']

    station_dfs = [pd.read_csv(path,delimiter='\t', dtype= {'minute':str,'hour':str,'date':str}) for path in filepaths ]

    ts_stations = pd.concat(station_dfs)

    # rename columns
    ts_stations.rename(columns={'dock_id':'station_id','dock_name':'station_name'},inplace=True)

    #assign am/pm
    ts_stations.pm = np.where(ts_stations.pm == 1, 'PM','AM')

    #convert to datetime objects
    ts_stations.minute = ts_stations.minute.map(lambda x:x.zfill(2))
    ts_stations.hour = ts_stations.hour.map(lambda x:x.zfill(2))
    ts_stations['date_time'] = ts_stations.apply(lambda x: x['date'] + " " + str(x['hour']) + ":" + str(x['minute']) + x['pm'],
                                                    axis=1)
    ts_stations.date_time = pd.to_datetime(ts_stations.date_time, format='%y-%m-%d %I:%M%p') 

    #add percent_full
    ts_stations['percent_full'] = ts_stations.avail_bikes/ts_stations.tot_docks

    #add seasons
    ts_stations['month'] = ts_stations.date_time.map(lambda x:x.month)

    def season(x):
        if x >=3 and x <=5:
            return 'spring'
        elif x >=6 and x <=8:
            return 'summer'
        elif x >=9 and x <=11:
            return 'fall'
        else:
            return 'winter'

    ts_stations['season'] = ts_stations.month.map(lambda x:season(x))

    #multihierarchical index times series
    ts_stations.set_index(['station_id','date_time'],inplace=True)
    ts_stations.sort_values(['station_id','date_time'],inplace=True)

    #drop uneeded cols
    ts_stations.drop(columns=['month','pm','hour','minute','date'],inplace=True)

    return ts_stations

def pickle_data():
    """
    Sends data to pickle for later use
    """

    live = station_initalize()
    starts, ends = trip_initialize()
    historical = historical_initalize()


    pickle_out = open('live.pickle','wb')
    pickle.dump(live, pickle_out)
    pickle_out.close()

    pickle_out = open('starts.pickle','wb')
    pickle.dump(starts,pickle_out)
    pickle_out.close()

    pickle_out = open('ends.pickle','wb')
    pickle.dump(ends,pickle_out)
    pickle_out.close()

    pickle_out = open('historical.pickle','wb')
    pickle.dump(historical,pickle_out)
    pickle_out.close()

def get_clean_data():
    """
    Returns clean data of start trips, end trips, historical stations and live stations
    """
    live = station_initalize()
    starts, ends = trip_initialize()
    historical = historical_initalize()

    return starts, ends, historical, live    
