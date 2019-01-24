from flask import Flask, g
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
from config import config_app
from layout import app_layout, make_left, make_right
from plots import process_data, plot_poster, hallo
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


@app.callback(Output('athlete', 'value'),
            [Input('url', 'pathname')],
            [State('athlete', 'value')])
def athltete_login(pathname, athlete):
    """Get athlete info and set it to the athlete div"""
    if pathname == '/' or pathname is None:
        rv = athlete
    else:
        try:
            _id = pathname.strip('/')
            r = requests.get('http://api:5042/athlete', params={'id': _id})
            rv = r.text
        except Exception as e:
            app.server.logger.error(e)
            rv = athlete
    app.server.logger.info(f"athltete_login: {rv}")
    return rv


@app.callback(Output('page-left', 'children'),
            [Input('url', 'pathname'),
             Input('athlete', 'value')])
def render_left(pathname, athlete):
    """Render left page based on value of pathname and athlete"""
    app.server.logger.info(f"render_left: {pathname} {athlete}")
    if (pathname == '/') or (athlete is None):
        rv = make_left()
    else:
        rv = hallo(json.loads(athlete))
    return rv


@app.callback(Output('interval-data', 'interval'),
             [Input('data', 'value')],
             events=[Event('interval-data', 'interval')])
def stop_interval_data(data):
    """Stop the interval, when data is loaded into page-right"""
    if data: # Stop the interval, when data is fetched
        app.server.logger.info(f"stop_interval_data True={(data is not None)} {type(data)} 3600 * 1000")
        return 3600 * 1000
    else:
        app.server.logger.info(f"stop_interval_data True={(data is None)} {type(data)} 1000")
        return 1000


@app.callback(Output('data', 'value'),
             [Input('athlete', 'value')],
              events=[Event('interval-data', 'interval')])
def fetch_data(athlete):
    """Load the data from API into the page right"""
    
    if athlete is not None:
        a = json.loads(athlete)
        _id = a.get('id', None)
    else:
        _id = None

    r = requests.get('http://api:5042/data', params={'id': _id})
    if r.text == "{}":
        app.server.logger.info(f"fetch_data: id: {_id} data: {r.text}")
        rv = None
    else:
        app.server.logger.info(f"fetch_data: id: {_id} data: {r.text[:240]}")
        rv = r.text
    return rv

@app.callback(Output('graph', 'value'),
     [Input('data', 'value')])
def fetch_graph(data):
    """Generate graph"""
    if data:
        _d = json.loads(data)
        app.server.logger.info(f'fetch_graph: Data {len(_d)}')
        d = process_data(_d)
        rv = plot_poster(d)
    else:
        app.server.logger.info(f'fetch_graph: No data')
        rv = None
    return rv


@app.callback(Output('page-right', 'children'),
            [Input('graph', 'value')],
             [State('page-right', 'children')])
def page_right(graph, children):
    """Load the data from API into the page right"""
    if graph:
        app.server.logger.info(f"page_right {type(graph)}")
        rv = html.Div(dcc.Graph(id='fig', figure=graph))
    else:
        app.server.logger.info(f"page_right Graph is not ready")
        rv = children
    return rv


if __name__ == '__main__':

    app.run_server(debug=True)
