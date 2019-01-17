from flask import Flask
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
from config import config_app
from layout import app_layout, make_left, make_right
from plots import bar_plot, scatter_plot
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


@app.callback(Output('page-left', 'children'), [Input('url', 'pathname')])
def routing(pathname):
    """Very basic router

    This callback function will read the current url
    and based on pathname value will populate the children of the page-main

    Returns:
        html.Div
    """
    app.server.logger.info(pathname)

    if pathname == '/':
        rv = make_left()
    else:
        rv = html.Div(pathname)

    return rv


@app.callback(Output('interval', 'interval'),
             [Input('page-right', 'value'), Input('url', 'pathname')])
def stop_interval(value, pathname):
    if value == html.Div("None") or pathname == '/':
        app.server.logger.info(f"{value} 1000")
        return 1000
    else:
        app.server.logger.info(f"{value} 3600")
        return 3600 * 1000


@app.callback(Output('page-right', 'children'),
             [Input('url', 'pathname')],
             [State('page-right', 'children')],
              events=[Event('interval', 'interval')])
def display_status(pathname, children):
    r = requests.get('http://api:5042/data')
    if r.text == 'None' or pathname == '/':
        app.server.logger.info(r.text)
        rv = children
    else:
        d = json.loads(r.text)
        app.server.logger.info(f"Data: {len(d)}")
        rv = html.Div(r.text)
    return rv


# @app.callback(Output('page-right', 'children'), [Input('url', 'pathname')])
# def routing_right(pathname):
#     """Very basic router

#     This callback function will read the current url
#     and based on pathname value will populate the children of the page-main

#     Returns:
#         html.Div
#     """
#     app.server.logger.info(pathname)

#     if pathname == '/':
#         rv = make_right()
#     else:
#         r = requests.get('http://api:5042/data')
#         rv = html.Div(r.text)

#     return rv


if __name__ == '__main__':

    app.run_server(debug=True)
