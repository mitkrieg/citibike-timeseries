import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from layouts import gcomponents
from app import app
from src.cleaning import station_initalize
import json
from datetime import datetime as dt

from numpy import nan
from pickle import load
import plotly.express as px

live = station_initalize()
system_daily = load(open('./data/pickle/system_daily.pickle','rb'))

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab"),
)
def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input, and 
    renders the associated graph with the tab name.
    """
    if active_tab is not None:
        if active_tab == "week-line":
            return dcc.Graph(figure=gcomponents['week_line'])
        elif active_tab == "week-heat":
            return dcc.Graph(figure=gcomponents['week_heat'])
    return "No tab selected"

@app.callback(
    Output("station-content","children"),
    Input("station-map","hoverData")
)
def render_station_content(hover_data):
    """
    This call back generates individual station information from cursor hover
    over the station map
    """
    name = hover_data['points'][0]['hovertext']
    station_id = hover_data['points'][0]['customdata'][0]
    lat = hover_data['points'][0]['lat']
    lon = hover_data['points'][0]['lon']
    status = 'Active'
    daily = px.line(system_daily['2018-06-17']['daily_'+station_id])

    try:
        capacity = live.loc[live.station_id == int(station_id)].capacity.values[0]
    except:
        capacity = ''
        status = 'Station no longer in Use'

    try:
        avail_bikes = live.loc[live.station_id == int(station_id)].num_bikes_available.values[0]
    except:    
        avail_bikes = ''
    
    try:
        avail_docks = live.loc[live.station_id == int(station_id)].num_docs_available.values[0]
    except:    
        avail_docks = ''
    
    try:
        disabled_bikes = live.loc[live.station_id == int(station_id)].num_bikes_disabled.values[0]
    except:
        disabled_bikes = '' 

    try:   
        disabled_docks = live.loc[live.station_id == int(station_id)].num_docks_disabled.values[0]
    except:    
        disabled_docks = ''
        
    try:
        action = live.loc[live.station_id == int(station_id)].bike_angels_action.values[0]
    except:
        action = ''

    try:       
        points = abs(live.loc[live.station_id == int(station_id)].bike_angels_points.values[0])
    except:
        points = ''   
        
    try:
        percent = avail_bikes / (capacity - disabled_bikes - disabled_docks)
    except:
        percent = nan   
        
        
    try:
        updated = dt.fromtimestamp(live.loc[live.station_id == int(station_id)].last_reported.values[0]).strftime('%a, %b %d %I:%M %p')
    except:
        updated = 'December 2018'

    basic_stats = dbc.Col(
        [
            html.H5('Basic Information'),
            html.P([
                'Station Name: ', name,
                html.Br(),
                'Station ID: ', station_id,
                html.Br(),
                'Coordinates: (', lat, ', ', lon,')',
                html.Br(),
                'Status: ', status,
                html.Br()
            ])
        ],
    )

    bike_stats = dbc.Col(
        [
            html.H5('Bike Stats'),
            html.P([
                'Last Reported: ', updated,
                html.Br(),
                html.Br(),
                'Capacity: ', capacity,
                html.Br(),
                'Available Bikes: ', avail_bikes,
                html.Br(),
                'Available Docks: ', avail_docks,
                html.Br(),
                'Disabled Bikes: ', disabled_bikes,
                html.Br(),
                'Disabled Docks: ', disabled_docks,
                html.Br(),
                'Percent Full: ', round(percent*100, 1), '%', 
                html.Br(),
                html.Br(),
                'Bike Angel Action: ', action,
                html.Br(),
                'Bike Angel Points: ', points
            ])
        ],
    )

    daily  = dbc.Col(
        [
            html.H5('Daily Seasonality'),
            dcc.Graph(figure=daily)
        ]
    )

    return basic_stats, bike_stats, daily
