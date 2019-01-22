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


@app.callback(Output('athlete', 'value'), [Input('url', 'pathname')],
              [State('athlete', 'value')])
def loging(pathname, athlete):
    """Get athlete info"""
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
    [Input('url', 'pathname'), Input('athlete', 'value')])
def render_left(pathname, athlete):
    """Render left page
    """
    app.server.logger.info(pathname)

    if pathname == '/' or athlete is None:
        rv = make_left()
    else:
        rv = athlete
    return rv


@app.callback(Output('data', 'value'),
             [Input('url', 'pathname'), Input('athlete', 'value')],
             [State('data', 'value')],
              events=[Event('interval-data', 'interval')])
def fetch_data(pathname, athlete, data):
    """Load the data from API into the page right"""
    if pathname == '/' or athlete is None:
        # do nothing
        rv = data
    else:
        app.server.logger.info(f"Fetch data: {athlete}")
        a = json.loads(athlete)
        r = requests.get('http://api:5042/data', params={'id': a.get('id', None)})
        rv = r.text
    return rv


@app.callback(Output('graph', 'value'),
             [Input('data', 'value')],
              events=[Event('interval', 'interval')])
def graph(data):
    """Generate graph"""
    if data is None:
        rv = None
    else:
        # load the data
        d = process_data(json.loads(data))
        rv = plot_poster(d)
    return rv



@app.callback(Output('page-right', 'children'),
             [Input('url', 'pathname'), Input('graph', 'value')],
             [State('page-right', 'children')],
              events=[Event('interval-graph', 'interval')])
def page_right(pathname, graph, children):
    """Load the data from API into the page right"""
    if pathname == '/':
        # do nothing
        app.server.logger.info(f"Page right 1: {pathname}")
        rv = children
    else:
        if graph is None:
            app.server.logger.info(f"Page right 2: {pathname}")
            rv = html.Div('Loading data')
        else:
            # load the data
            app.server.logger.info(f"Page right 3: {pathname} graph ok")
            # g = json.loads(graph)
            rv = html.Div(dcc.Graph(id='fig', figure=graph))
    return rv


@app.callback(Output('interval-data', 'interval'),
             [Input('data', 'value'), Input('url', 'pathname')])
def stop_interval_data(data, pathname):
    """Stop the interval, when data is loaded into page-right"""
    if (data is None) or (pathname == '/'):
        app.server.logger.info(f"Data 1000")
        return 1000
    else:
        app.server.logger.info(f"Data 3600 * 1000")
        return 3600 * 1000


@app.callback(Output('interval-graph', 'interval'),
             [Input('graph', 'value'), Input('url', 'pathname')])
def stop_interval_graph(graph, pathname):
    """Stop the interval, when data is loaded into page-right"""
    if (graph is None) or (pathname == '/'):
        app.server.logger.info(f"Graph 1000")
        return 1000
    else:
        app.server.logger.info(f"Graph 3600 * 1000")
        return 3600 * 1000




if __name__ == '__main__':

    app.run_server(debug=True)
