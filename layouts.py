import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from app import app
import plotly.express as px

import pandas as pd

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
# Reusable Components
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
# Page Layout
#####################################

### System
system_layout = dbc.Container([
    html.Div(
        [
            html.H2('System Stats'),
            html.Div(
                [
                    html.Img(src=app.get_asset_url('cibike_logo.png')),
                    html.Div([html.H4('test'),html.P('body')])
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
