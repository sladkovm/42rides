from flask import Flask, g
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
from config import config_app
from layout import app_layout, make_left, make_right
from plots import process_data, plot_poster
import time
import requests
import json

import sys


server = Flask(__name__)


app = dash.Dash(name='Bootstrap_docker_app',
                server=server,
                static_folder='static',
                csrf_protect=False)

# Add css, js, container div with id='page-content' and location with id='url'
app = config_app(app, debug=True)

# Generate app layoute with 3 div elements: page-header, page-main, page-footer.
# Content of each div is a function input
app.layout = app_layout()


@app.callback(Output('athlete', 'children'), [Input('url', 'pathname')],
              [State('athlete', 'children')])
def loging(pathname, athlete):
    if pathname == '/' or pathname is None:
        rv = athlete
    else:
        try:
            id = pathname.strip('/')
            r = requests.get('http://api:5042/athlete', params={'id': id})
            app.server.logger.info(f"Loging: {r.text}")
            rv = r.text
        except Exception as e:
            app.server.logger.error(e)
            rv = athlete
    return rv


@app.callback(Output('page-left', 'children'),
    [Input('url', 'pathname'), Input('athlete', 'children')])
def render_left(pathname, athlete):
    """Very basic router

    This callback function will read the current url
    and based on pathname value will populate the children of the page-main

    Returns:
        html.Div
    """
    app.server.logger.info(pathname)

    if pathname == '/' or athlete is None:
        rv = make_left()
    else:
        rv = athlete
    return rv


@app.callback(Output('interval', 'interval'),
             [Input('page-right', 'value'), Input('url', 'pathname')])
def stop_interval(value, pathname):
    """Stop the interval, when data is loaded into page-right"""
    if value == html.Div("None") or pathname == '/':
        app.server.logger.info(f"{value} 1000")
        return 1000
    else:
        app.server.logger.info(f"{value} 3600")
        return 3600 * 1000


@app.callback(Output('page-right', 'children'),
             [Input('url', 'pathname'), Input('athlete', 'children')],
             [State('page-right', 'children')],
              events=[Event('interval', 'interval')])
def display_status(pathname, athlete, children):
    """Load the data from API into the page right"""
    if pathname == '/' or athlete is None:
        # do nothing
        rv = children
    else:
        app.server.logger.info(f"Display: {athlete}")
        a = json.loads(athlete)
        r = requests.get('http://api:5042/data', params={'id': a.get('id', None)})
        # load the data
        d = json.loads(r.text)
        data = process_data(d)
        rv = html.Div(dcc.Graph(id='fig', figure=plot_poster(data)))
        # rv = r.text
    return rv


if __name__ == '__main__':

    app.run_server(debug=True)
