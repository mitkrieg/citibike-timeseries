import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from pickle import load

#####################################
# Data
#####################################

starts = load(open('./data/pickle/starts.pickle','rb'))

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
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
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
week_line.update_layout(title='Average Number of Rides per Hour',
                 xaxis_title='Hour',
                 yaxis_title='Number of Rides')


gcomponents = {'week_line':week_line}
#### Weekly heatmap

#####################################
# Page Layout
#####################################

### System
system_layout = dbc.Container([
    html.Div(
        [
            html.H2('System Stats'),
            html.Div(
                [
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
            )
            
            
        ],
        id='page-content'
    ), 
])

### Station
station_layout = dbc.Container([
    html.Div(
        [
            html.H2('Station Stats')
        ],
        id='page-content'
    )
])
