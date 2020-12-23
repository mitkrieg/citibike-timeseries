import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import json, os
import pickle

############ Setup ###################

#retreive data
year_2018 = pickle.load(open('./pickle/historical.pickle','rb'))


#get sytlesheet and instantiate app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True)

#color scheme
colors = {
    'background': '#111111',
    'heading': '#7FDBFF',
    'text': \12
}

#get mapbox API key for geoplotting
path = '/Users/mitchellkrieger/.secret/mapbox_api.json'

with open(path) as f:
    api = json.load(f)
    
api_key = api['api_token']

px.set_mapbox_access_token(api_key)

############ Contents ###################

# Overview Text
md_text = """
## Overview

Citibike and other similar bike-sharing systems face a unique challenge in balancing their system. Bikes must be distributed across all stations so that riders have access to both bikes to take out and empty docks to return bikes to. Unchecked, this challenge may cause bikes to pool in a certain station and drain from others. This project attempts to understand which stations in the Citibike system are pools, drains, or balanced. To do this, time series analysis was used to predict the number of bikes at a given station given the time and then based on their extracted daily seasonality from the time series model, 
classify stations as pools, drains, or balanced.
"""

# # prepdata for geographic plotting
# hours = year_2018.groupby([pd.Grouper(freq='H',level='date_time'),
#                   pd.Grouper(level='station_id')]).mean()
# hours['id']=[i[1] for i in list(hours.index)]
# hours['dt']=[str(i[0]) for i in list(hours.index)]

# #slice a particular 2 weeks to plot
# hours_slice = hours.xs(slice('2018-06-17','2018-06-30'),level=-2)

# percent_map = px.scatter_mapbox(hours_slice, lat="_lat", lon="_long",
#                         animation_frame='dt', animation_group='id',
#                         color="percent_full", size="avail_bikes",
#                         color_continuous_scale=px.colors.cyclical.IceFire, size_max=15,
#                         zoom=10,width=800,height=800)


# percent_map.update_layout(
#     plot_bgcolor=colors['background'],
#     paper_bgcolor=colors['background'],
#     font_color=colors['text']
# )

############ Construct App ###################

#layout
app.layout = html.Div(style={'backgroundColor': colors['background']},children=[
    html.Div(html.Img(src=app.get_asset_url('citibike_logo.png'), style={'width':'50%'}),
        style={'textAlign':'center'}
    ),
    html.H1('System Diagnostics & Rebalancing',
            style={
            'textAlign': 'center',
            'color': colors['heading']
        }
    ),
    dcc.Markdown(children=md_text,style={'color':colors['text']}),

    html.Div(style={'backgroundColor': colors['background']},children=[
        dcc.Tabs(id='tabs', value='stations-tab', children=[
            dcc.Tab(label='Stations', value='stations-tab'),
            dcc.Tab(label='System', value='system-tab')
        ]), 

        html.Div(id='tab-content') 
    ])
    

])

# callbacks
@app.callback(Output('tab-content','children'),
              Input('tabs','value')  
)
def render_content(tab):
    if tab == 'stations-tab':
        return html.Div(style={'color':colors['background']},children=[
            html.Div(style={'color':colors['background']}, children=[
                html.Div(style={'float':'left','margin':'auto',
                        'color':colors['background'],'textAlign':'center'}, children=[
                    html.H4('Station Map', style={'textAlign':'center','color':colors['text']}),
                    dcc.Dropdown(id='station-drop', options=[
                        {'label':'Percent Full Map', 'value':'percent'},
                        {'label':'Cluster Map','value':'cluster'}],
                        value='cluster',
                        clearable=False),
                    html.Div(id='map-content')],
                    ),
                html.Div(id='station-stats', style={'float':'right','margin':'auto',
                        'color':colors['background'],'textAlign':'center'},children=[
                    html.H4('Station Stats')
                    ])
            ])
        ])
    elif tab == 'system-tab':
        return html.Div([
            html.H3('System Stuff goes Here')
        ])

@app.callback(Output('map-content','children'),
              Input('station-drop','value')
)
def render_map(map):
    if map == 'percent':
        return html.Div([html.H4('Percent Map Goes Here')])
    elif map == 'cluster':
        return html.Div([html.H4('Cluster Map Goes Here')])
    

if __name__ == '__main__':
    app.run_server(port=5000, host= '127.0.01',debug=True)