import dash_core_components as dcc
import dash_html_components as html
from app import app

#####################################
# Styles & Colors
#####################################



#####################################
# Reusable Components
#####################################

def nav_bar():

    nav_bar = html.Div([
        
        html.Div([
            html.Img(
                src  = app.get_asset_url('citibike_logo.png'),
                height = '40px',
                style = {'padding-top':'5%',
                        'padding-left':'5%'
                }
            )],
            className = 'col-2',
        ),

        html.Div([
            html.H1('System Performance Dashboard')],
            className='col-10'),
        
        ],

        className = 'row',
        style = {'height':'4%'} 
        )
    return nav_bar


layout1 = html.Div([
    nav_bar(),
    html.H3('App 1'),
    dcc.Dropdown(
        id='app-1-dropdown',
        options=[
            {'label': 'App 1 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    html.Div(id='app-1-display-value'),
    dcc.Link('Go to App 2', href='/apps/app2')
])

layout2 = html.Div([
    html.H3('App 2'),
    dcc.Dropdown(
        id='app-2-dropdown',
        options=[
            {'label': 'App 2 - {}'.format(i), 'value': i} for i in [
                'NYC', 'MTL', 'LA'
            ]
        ]
    ),
    html.Div(id='app-2-display-value'),
    dcc.Link('Go to App 1', href='/apps/app1')
])
