import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from layouts import gcomponents
from app import app
import json

@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab"),
)
def render_tab_content(active_tab):
    """
    This callback takes the 'active_tab' property as input, as well as the
    stored graphs, and renders the tab content depending on what the value of
    'active_tab' is.
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
    name = hover_data['points'][0]['hovertext']
    station_id = hover_data['points'][0]['customdata'][0]
    lat = hover_data['points'][0]['lat']
    lon = hover_data['points'][0]['lon']

    basic_stats = html.Div(
        [
            html.P([
                'Station Name: ', name,
                html.Br(),
                'Station ID: ', station_id,
                html.Br(),
                'Coordinates: (', lat, ', ', lon,')'])
        ]
    )

    return basic_stats
