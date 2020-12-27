import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from layouts import gcomponents
from app import app

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
            #return dcc.Graph(figure=gcomponents['week_line'])
            return html.P("line graph goes here")
        elif active_tab == "week-heat":
            #return dcc.Graph(figure=gcomponents['week_heat'])
            return html.P('heatmap goes here')
    return "No tab selected"

