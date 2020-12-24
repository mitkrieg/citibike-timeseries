import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from layouts import system_layout, station_layout, nav_bar, CONTENT_STYLE
import callbacks

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    nav_bar(),
    html.Div(id='page-content',style=CONTENT_STYLE)
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return system_layout
    elif pathname == '/system':
         return system_layout
    elif pathname == '/station':
         return station_layout
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(port=5000, host= '127.0.01',debug=True)