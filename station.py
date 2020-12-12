import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
from pickle import load, dump
from cleaning import *

from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_pacf, plot_acf

def search_station_id(query):
    """
    Returns station ids given a particular string as query
    """
    live = load(open('live.pickle','rb'))
    return live.loc[live.station_name.str.contains(query)][['station_name','station_id']]

def search_station_id(query):
    """
    Returns station name given a particular id as query
    """
    live = load(open('live.pickle','rb'))
    return live.loc[live.station_id == int(query)][['station_id','station_name']]

def get_lon_lat(id):
    """
    Returns Longitude and Latitude coordinates as a tuple given a station id
    """
    live = load(open('live.pickle','rb'))
    return (live.loc[live.station_id == id].lat.values[0], live.loc[live.station_id == id].lon.values[0])

class Station(object):
    
    live = load(open('live.pickle','rb'))
    starts = load(open('starts.pickle','rb'))
    ends = load(open('ends.pickle','rb'))
    historical = load(open('historical.pickle','rb'))

    def __init__(self, station_id):
        self.id = station_id
        self.name = self.live.loc[self.live.station_id == station_id].station_name.values[0]
        self.ts_starts = self.starts.loc[int(station_id)]
        self.ts_ends = self.ends.loc[int(station_id)]
        self.ts_bikes = self.historical.loc[int(station_id)]
        self.lat = self.live.loc[self.live.station_id == station_id].lat.values[0]
        self.lon = self.live.loc[self.live.station_id == station_id].lon.values[0]
        self.capacity = self.live.loc[self.live.station_id == station_id].capacity.values[0]
        self.station_type = self.live.loc[self.live.station_id == station_id].station_type.values[0]
        self.legacy_id = self.live.loc[self.live.station_id == station_id].legacy_id_x.values[0]
        self.has_kiosk = self.live.loc[self.live.station_id == station_id].has_kiosk.values[0]
        self.region_id = self.live.loc[self.live.station_id == int(station_id)].region_id.values[0]
        self.region_name = regions[self.region_id]
        self.current_avail_bikes = self.live.loc[self.live.station_id == station_id].num_bikes_available.values[0]
        self.current_disabled_bikes = self.live.loc[self.live.station_id == station_id].num_bikes_disabled.values[0]
        self.current_avail_docks = self.live.loc[self.live.station_id == station_id].num_docks_available.values[0]
        self.current_disabled_docks = self.live.loc[self.live.station_id == station_id].num_docks_disabled.values[0]
        self.status = self.live.loc[self.live.station_id == station_id].station_status.values[0]
        self.rental_methods = self.live.loc[self.live.station_id == station_id].rental_methods.values[0]
        self.last_update = dt.datetime.fromtimestamp(self.live.loc[self.live.station_id == station_id].last_reported.values[0])
        
    
    def info(self):
        """
        Prints basic station stats
        """
        print(f"""
        #### Station {self.id} Info ####
        
        Name: {self.name}
        Status: {self.status}
        Legacy ID: {self.legacy_id}
        Type: {self.station_type}
        Region: {self.region_name} 
        Coordinates: ({self.lat},{self.lon})
        Rental Methods: {self.rental_methods}
        Has Kiosk: {self.has_kiosk}
        
        #### Bike Stats ####
        
        As of: {self.last_update}
        Capacity: {self.capacity}
        Available Bikes: {self.current_avail_bikes}
        Available Docks: {self.current_avail_docks}
        Disabled Bikes: {self.current_disabled_bikes}
        Disabled Docks: {self.current_disabled_docks}
        """)
    
    def net_bikes_ts(self, resample='H'):
        """
        Returns a pandas Time Series of net bikes in/out per resample time period
        Positive value indicates net gain of bikes over resample time period 
        Negative value indicates net loss of bikes over resample time period
        
        ---Params---
    
        resample: str, pandas date offset string, defaults to hourly ('H')
                    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 
        """
        return self.ts_ends.resample(resample).tripduration.count() \
            - self.ts_starts.resample(resample).tripduration.count()
    
    def avail_bikes_ts(self, resample='H', time_interval=None):
        """
        Returns a pandas Time Series of average available bikes at station per resample time period
        
        ---Params---
        
        resample: str, pandas date offset string, defaults to hourly ('H')
                    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 
        
        time_interval: ('YYYY-MM-DD HH:MM','YYYY-MM-DD HH:MM'), tuple of 2 strings, if None defaults to entire time series
        """
        if time_interval == None:
            return self.historical.loc[self.id].avail_bikes.resample(resample).mean()
        else:
            return self.historical.loc[self.id].avail_bikes.resample(resample).mean()[time_interval[0]:time_interval[1]]
    
    def plot_net_bikes(self, resample='H', time_interval=None):
        """
        Plots the Net Bikes in/out of a station over a given time interval by resample size
        Positive value indicates net gain of bikes over resample time period 
        Negative value indicates net loss of bikes over resample time period
        
        ---Params---
        
        resample: str, pandas date offset string, defaults to hourly ('H')
                    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 

        time_interval: ('YYYY-MM-DD HH:MM','YYYY-MM-DD HH:MM'), tuple of 2 strings, if None defaults to entire time series
        """
        station_net = self.net_bikes_ts(resample)
        fig, ax = plt.subplots(figsize=(10,5))
        if time_interval == None:
            ax.plot(station_net)
            ax.set_title(f'Net Bikes ({resample})\nStation {self.id}: {self.name}')
            return ax
        else:
            ax.plot(station_net[time_interval[0]:time_interval[1]])
            ax.set_title(f'Net Bikes ({resample})\nStation {self.id}: {self.name}')
            return ax
            
    def plot_avail_bikes(self,resample='H',time_interval=None):
        """
        Plots the total average Bikes available at a station over a given time interval by resample size
        
        ---Params---

        resample: str, pandas date offset string, defaults to hourly ('H')
                    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 

        time_interval: ('YYYY-MM-DD HH:MM','YYYY-MM-DD HH:MM'), tuple of 2 strings, if None defaults to entire time series
        """
        station_avail = self.avail_bikes_ts(resample)
        fig, ax = plt.subplots(figsize=(10,5))
        if time_interval == None:
            ax.plot(station_avail)
            ax.set_title(f'Total Bikes ({resample})\nStation {self.id}: {self.name}')
            return ax
        else:
            ax.plot(station_avail[time_interval[0]:time_interval[1]])
            ax.set_title(f'Total Bikes ({resample})\nStation {self.id}: {self.name}')
            return ax
        
    def availbike_stationarity(self,resample='H',time_interval=None, window = 6):
        """
        Checks the stationarity of time series with rolling mean, rolling std and dickey fuller test
        
        ---Params---
        
        resample: str, pandas date offset string, defaults to hourly ('H')
                    https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 

        time_interval: tuple of 2 strings, ('YYYY-MM-DD HH:MM','YYYY-MM-DD HH:MM'), if None defaults to entire time series
        
        window: int, window used in rolling calculation
        """
        if time_interval == None:
            ts = self.avail_bikes_ts(resample=resample)
        else:
            ts = self.avail_bikes_ts(resample=resample)[time_interval[0]:time_interval[1]]
        
        #Plot time series, rolling mean, rolling std
        roll_mean = ts.rolling(window=window).mean()
        roll_std = ts.rolling(window=window).std()
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(ts);
        ax.plot(roll_mean)
        ax.plot(roll_std)
        ax.legend(['Time Series','Roll Mean','Roll STD'])
        
        #Dickey Fuller
        dftest = adfuller(ts)

        # Extract and display test results
        dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
        for key,value in dftest[4].items():
            dfoutput['Critical Value (%s)'%key] = value
    
        print ('Dickey-Fuller test: \n')
        print(dfoutput)
        
        if dfoutput['p-value'] < .05:
            print(f'\nStationary: p-value {dfoutput["p-value"]} < 0.05')
        else:
           print(f'\nNot Stationary: p-value {dfoutput["p-value"]} > 0.05')
               
        return roll_mean, roll_std, ax, dfoutput
    
    def availbike_decompose(self, resample='H',time_interval=None):
        """
        Performs decompostion of Available Bikes time seres
        
        ---Params---
        
        resample: str, pandas date offset string, defaults to hourly ('H')
                https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 

        time_interval: tuple of 2 strings, ('YYYY-MM-DD HH:MM','YYYY-MM-DD HH:MM'), if None defaults to entire time series
        """
        if time_interval == None:
            ts = self.avail_bikes_ts(resample=resample)
        else:
            ts = self.avail_bikes_ts(resample=resample)[time_interval[0]:time_interval[1]]
            
        decomposition = seasonal_decompose(ts)

        trend = decomposition.trend
        seasonal = decomposition.seasonal
        residuals = decomposition.resid
        
        plt.figure(figsize=(12,8))
        plt.subplot(411)
        plt.plot(ts,label='Original',color='blue')
        plt.legend(loc='upper left')
        plt.subplot(412)
        plt.plot(trend,label='Trend',color='green')
        plt.legend(loc='upper left')
        plt.subplot(413)
        plt.plot(seasonal,label='Seasonal',color='orange')
        plt.legend(loc='upper left')
        plt.subplot(414)
        plt.plot(residuals,label='Residuals',color='red')
        plt.legend(loc='upper left')
        
        return decomposition

    def netbike_stationarity(self,resample='H',time_interval=None, window = 6):
        """
        Checks the stationarity of net bike time series with rolling mean, rolling std and dickey fuller test
        
        ---Params---
        
        resample: str, pandas date offset string, defaults to hourly ('H')
                https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 

        time_interval: tuple of 2 strings, ('YYYY-MM-DD HH:MM','YYYY-MM-DD HH:MM'), if None defaults to entire time series
        
        window: int, window used in rolling calculation
        """
        if time_interval == None:
            ts = self.net_bikes_ts(resample=resample)
        else:
            ts = self.net_bikes_ts(resample=resample)[time_interval[0]:time_interval[1]]
        
        #Plot time series, rolling mean, rolling std
        roll_mean = ts.rolling(window=window).mean()
        roll_std = ts.rolling(window=window).std()
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(ts);
        ax.plot(roll_mean)
        ax.plot(roll_std)
        ax.legend(['Time Series','Roll Mean','Roll STD'])
        
        #Dickey Fuller
        dftest = adfuller(ts)

        # Extract and display test results
        dfoutput = pd.Series(dftest[0:4], index=['Test Statistic', 'p-value', '#Lags Used', 'Number of Observations Used'])
        for key,value in dftest[4].items():
            dfoutput['Critical Value (%s)'%key] = value
    
        print ('Dickey-Fuller test: \n')
        print(dfoutput)
        
        if dfoutput['p-value'] < .05:
            print(f'\nStationary: p-value {dfoutput["p-value"]} < 0.05')
        else:
           print(f'\nNot Stationary: p-value {dfoutput["p-value"]} > 0.05')
               
        return roll_mean, roll_std, ax, dfoutput
    
    def netbike_decompose(self, resample='H',time_interval=None):
        """
        Performs decompostion of Available Bikes time seres
        
        ---Params---
        
        resample: str, pandas date offset string, defaults to hourly ('H')
                https://pandas.pydata.org/pandas-docs/stable/user_guide/timeseries.html#dateoffset-objects 

        time_interval: tuple of 2 strings, ('YYYY-MM-DD HH:MM','YYYY-MM-DD HH:MM'), if None defaults to entire time series
        """
        if time_interval == None:
            ts = self.net_bikes_ts(resample=resample)
        else:
            ts = self.net_bikes_ts(resample=resample)[time_interval[0]:time_interval[1]]
            
        decomposition = seasonal_decompose(ts)

        trend = decomposition.trend
        seasonal = decomposition.seasonal
        residuals = decomposition.resid
        
        plt.figure(figsize=(12,8))
        plt.subplot(411)
        plt.plot(ts,label='Original',color='blue')
        plt.legend(loc='upper left')
        plt.subplot(412)
        plt.plot(trend,label='Trend',color='green')
        plt.legend(loc='upper left')
        plt.subplot(413)
        plt.plot(seasonal,label='Seasonal',color='orange')
        plt.legend(loc='upper left')
        plt.subplot(414)
        plt.plot(residuals,label='Residuals',color='red')
        plt.legend(loc='upper left')
        
        return decomposition     
    
    def update_bikes(self):
        """
        Updates bike & dock status at stations and returns new live bike df
        """
        df = station_initalize()
        live = df
        self.current_avail_bikes = df.loc[df.station_id == self.id].num_bikes_available
        self.current_disabled_bikes = df.loc[df.station_id == self.id].num_bikes_available
        self.current_avail_docks = df.loc[df.station_id == self.id].num_docks_available
        self.current_disabled_docks = df.loc[df.station_id == self.id].num_docks_disabled

        pickle_out = open('live.pickle','wb')
        pickle.dump(df,pickle_out)
        pickle_out.close()

        return df