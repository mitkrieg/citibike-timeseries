import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

md_text = """
## Overview

Citibike and other similar bike-sharing systems face a unique challenge in balancing their system. Bikes must be distributed across all stations so that riders have access to both bikes to take out and empty docks to return bikes to. Unchecked, this challenge may cause bikes to pool in a certain station and drain from others. This project attempts to understand which stations in the Citibike system are pools, drains, or balanced. To do this, time series analysis was used to predict the number of bikes at a given station given the time and then based on their extracted daily seasonality from the time series model, 
classify stations as pools, drains, or balanced.
"""

fig = px.bar(df, x="Fruit", y="Amount", color="City", barmode="group")

fig.update_layout(
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    font_color=colors['text']
)

app.layout = html.Div(style={'backgroundColor': colors['background']},children=[
    html.Div(html.Img(src=app.get_asset_url('citibike_logo.png'), style={'width':'50%'}),
        style={'textAlign':'center'}
    ),
    html.H1('System Diagnostics & Rebalancing',
            style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),
    dcc.Markdown(children=md_text,style={'color':font_color}),
    html.Div(id='my-output'),
    dcc.Graph(
        id='example-graph-2',
        figure=fig
    )
])


# @app.callback(
#     Output(component_id='my-output', component_property='children'),
#     Input(component_id='my-input', component_property='value')
# )
# def update_output_div(input_value):
#     return 'Output: {}'.format(input_value)


if __name__ == '__main__':
    app.run_server(port=5000, host= '127.0.01',debug=True)