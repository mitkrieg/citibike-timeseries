import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app
import plotly.express as px
import plotly.graph_objects as go

import boto3

import pandas as pd
import json
from pickle import load

#####################################
# Data
#####################################

starts = load(open('./data/starts.pickle','rb'))
animation_data = load(open('./data/june17_slice.pickle','rb'))
clusters = load(open('./data/clusters.pickle','rb'))

#####################################
# Styles & Colors
#####################################

NAVBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "top":0,
    "margin-left": "18rem",
    "margin-right": "2rem",
}

#####################################
# Components
#####################################

def nav_bar():

    navbar = html.Div(
    [
        html.Img(src=app.get_asset_url('citibike_logo.png'), 
                    style={'width':'100%','align':'center'}),
        html.H4("System Performance Dashboard", className="display-10",style={'textAlign':'center'}),
        html.Hr(),
        dbc.Nav(
            [
                dbc.NavLink("About", href="/about",active="exact"),
                dbc.NavLink("System", href="/system", active="exact"),
                dbc.NavLink("Station", href="/station", active="exact"),
            ],
            pills=True,
            vertical=True
        ),
    ],
    style=NAVBAR_STYLE,
    )
    
    return navbar

#####################################
# Graphical/data Components
#####################################

#### Weekday vs Weekend ####

#separate trips into weekdays and weekends
weekdays = starts[starts.weekday==True].droplevel(level=-2)
weekends = starts[starts.weekday==False].droplevel(level=-2)

ww = pd.concat([weekdays.groupby(weekdays.index.hour).size()/52/5,weekends.groupby(weekends.index.hour).size()/52/2],
              axis=1)
ww.rename(columns={0:'weekdays',1:'weekends'}, inplace=True)

week_line = go.Figure()
week_line.add_trace(go.Scatter(y=ww.weekdays,mode='lines',fill='tozeroy',name='Weekdays'))
week_line.add_trace(go.Scatter(y=ww.weekends,mode='lines',fill='tozeroy',name='Weekends'))
week_line.update_layout(
                 height=250,
                 xaxis_title='Hour',
                 yaxis_title='Average Number of Rides',
                 legend={
                     'yanchor':'top',
                     'y':.99,
                     'xanchor':'left',
                     'x':.01
                 },
                 margin={'l':5,'r':2,'t':5,'b':5}
                 )

#### Weekly heatmap ####

starts_by_weekday = starts.droplevel(level=-2)
starts_by_weekday = starts_by_weekday.groupby([starts_by_weekday.index.hour,'day_of_week']).size().unstack().transpose()

week_heat = px.imshow(starts_by_weekday,color_continuous_scale='hot')
week_heat.update_layout(
                 xaxis_title='Hour',
                 xaxis={'tickmode':'linear',
                        'tick0':0,
                        'dtick':1},
                 yaxis_title='Day',
                 yaxis={'tickmode':'array',
                        'tickvals':list(range(7)),
                        'ticktext':['Mon','Tues','Wed','Thurs','Fri','Sat','Sun']},
                 coloraxis_colorbar={'title':"Total Rides"},
                 margin={'l':5,'r':2,'t':5,'b':5})

#### Animated Map ####

#get mapbox API key for plotting
path = '/Users/mitchellkrieger/.secret/mapbox_api.json'

with open(path) as f:
    api = json.load(f)
    
api_key = api['api_token']

px.set_mapbox_access_token(api_key)

#plot 
animap = px.scatter_mapbox(animation_data, lat="_lat", lon="_long",
                        animation_frame='dt', animation_group='id',
                        color="percent_full", size="avail_bikes",
                        color_continuous_scale=px.colors.cyclical.IceFire, size_max=15,
                        zoom=10,width=600,height=650)

animap.update_layout(margin={'l':5,'r':2,'t':5,'b':5})


#### Cluster Map ####

clusters.reset_index(inplace=True)

cluster_map = px.scatter_mapbox(clusters, lat="_lat", lon="_long",
                        hover_name='station_name',hover_data=['station_id','_lat','_long'],
                        color='KMeans_5_named', zoom=11,width=400,height=650, 
                        labels={'KMeans_5_named':'Clusters'}, 
                        color_discrete_sequence=['red','darkorange','yellowgreen','forestgreen','dodgerblue'],
                        category_orders={'KMeans_5_named':['Pool',
                                                           'Slight Pool',
                                                           'Balanced - Residential',
                                                           'Balanced - Business District',
                                                           'Drain'
                                                          ]})

cluster_map.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01),
    margin={'l':5,'r':2,'t':5,'b':5}
    )


#### Histogram of trip duration ####

duration = starts.tripduration/60

duration_hist = px.histogram(duration, x='tripduration',range_x=[0,90], height=250)

duration_hist.update_layout(margin={'l':5,'r':2,'t':5,'b':5})

duration_hist.add_shape(type='line',
                        x0=30,
                        x1=30,
                        y0=0,
                        y1=1,
                        line={'color':'lightblue','dash':'dash'},
                        xref='x',
                        yref='paper')

duration_hist.add_shape(type='line',
                        x0=45,
                        x1=45,
                        y0=0,
                        y1=1,
                        line={'color':'red','dash':'dash'},
                        xref='x',
                        yref='paper')

#### Storing components for later use in callbacks.py####

gcomponents = {'week_line':week_line,
                'week_heat':week_heat,}


#####################################
# Page Layout
#####################################

### System
system_layout = html.Div([
    html.H2("System Stats"),
    html.Hr(),
    dbc.Container([
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                            html.H4('Weekly Traffic Analysis'),
                            dbc.Tabs(
                                [
                                    dbc.Tab(label='Line',tab_id='week-line'),
                                    dbc.Tab(label='Heat',tab_id='week-heat')
                                ],
                                id="tabs",
                                active_tab='week-line',
                                ),
                            html.Div(id="tab-content",className="p-4")
                            ]
                        ),
                        html.H4("Frequency of Ride Duration"),
                        dcc.Graph(figure=duration_hist)
                    ],
                    width=6
                ),
                
                dbc.Col(
                    [
                        html.H4('System Seasonality over typical 2 weeks'),
                        dcc.Graph(figure=animap)
                    ],
                    width=6
                )
                
            ],
        ), 
    ]),
], id='page-content')


### Station
station_layout = html.Div(
    [
        dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H4('Station Map (2018)'),
                                html.Hr(),
                                dcc.Graph(figure=cluster_map,
                                        id='station-map',
                                        clickData={'points':[{
                                            "hovertext":'None',
                                            "lat":"None",
                                            "lon":"None",
                                            "customdata":['72']}
                                        ]}
                                )
                            ],
                            width=5
                        ),
                        dbc.Col(
                            [
                                html.H4('Selected Station Info'),
                                html.Hr(),
                                dbc.Row(id='station-content'),
                                dbc.Row(id='forcast-graph'),
                                html.Div(id='daily-graph'),
                            ],
                        )
                    ]
                ),
            ]
        )
    ],
    id='page-content'
)


about_layout = dbc.Row(
    [
        dbc.Col(
            [
                html.H2('About this project'),
                html.P('Author: Mitchell Krieger'),
                dcc.Markdown('Contact: mitkrieger@gmail.com | [Project GitHub](https://github.com/mitkrieg/citibike-timeseries)'),
                dcc.Markdown('''### The Rebalancing Problem
                
Citibike and other similar bike-sharing systems face a unique challenge in managing their system. Bikes must be distributed across all stations so that riders have access to both bikes to take out and empty docks to return bikes to. Unchecked, this challenge may cause bikes to pool in a certain station and drain from others. This project attempts to understand which stations in the Citibike system are pools, drains, or balanced. 
                
### Methodology
                
To figure out how to best rebalance the system, first time series analysis was used to predict the number of bikes at a given station at a given time, Then based on extracted seasonality from the time series model, stations were classified as pools, drains, or balanced using clustering. Only data from 2018 was used because newer data was either unavailable or inconsistent. This means that system balance may have changed since the addition of nearly 500 new stations throughout NYC since 2018 and changes in rider behavior due to COVID-19.            
                ''')
            ]
        ),
        dbc.Col(
            [
                html.Img(src=app.get_asset_url('urban-bike-nyc-preview.jpg'),style={'width':'100%','align':'center','verticalAlign':'middle'}),
                html.Hr(),
                dcc.Markdown("""### This Dashboard

On the system page, you can see an overview of the 2018 system looking at typical weekly seasonality and legnth of trip duration. On the Station page, you can select a station from the map to see the time series model for each station, daily seasonality and current bike stats pulled from the live citibike data feed.
""")
            ],
            style={'verticalAlign':'middle'}
        )

    ],
    id='page-content'
)