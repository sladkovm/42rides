from flask import Flask, g
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
from dash.exceptions import PreventUpdate
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


@app.callback(Output('athlete', 'data'),
            [Input('url', 'pathname')],
            [State('athlete', 'data')])
def athltete_login(pathname, athlete):
    """Get athlete info and set it to the athlete div"""
    if pathname == '/' or pathname is None:
        raise PreventUpdate
    else:
        try:
            _id = pathname.strip('/')
            r = requests.get('http://api:5042/athlete', params={'id': _id})
            rv = r.text
        except Exception as e:
            app.server.logger.error(e)
            raise PreventUpdate
    app.server.logger.info(f"athltete_login: {rv}")
    return rv


@app.callback(Output('page-left', 'children'),
            [Input('url', 'pathname'),
             Input('athlete', 'modified_timestamp')],
             [State('athlete', 'data')])
def render_left(pathname, ts, athlete):
    """Render left page based on value of pathname and athlete"""
    if ts is None:
        raise PreventUpdate
    app.server.logger.info(f"render_left: {pathname} {athlete}")
    if (pathname == '/') or (athlete is None):
        rv = make_left()
    else:
        rv = hallo(json.loads(athlete))
    return rv


# @app.callback(Output('interval', 'interval'),
#              [Input('athlete', 'modified_timestamp'),
#               Input('graph', 'value'),
#               Input('interval', 'n_intervals')],
#              [State('athlete', 'data')])
# def stop_interval_data(tsa, graph, n_intervals, athlete):
#     """Stop the interval, when data is loaded into page-right"""
#     app.server.logger.info(f"stop_interval_data: tsa:{tsa}")
#     if (tsa is None):
#         raise PreventUpdate
#     if (athlete is not None) and (graph is None):
#         app.server.logger.info(f"stop_interval_data: tsa:{tsa} Start interval")
#         return 1000
#     elif graph is not None:
#         app.server.logger.info(f"stop_interval_data: tsa:{tsa} Stop interval")
#         return 3600 * 1000
#     else:
#         raise PreventUpdate
    # if (tsa is None):
    #     # do not run interval, when all is None
    #     app.server.logger.info(f"stop_interval_data tsa:{tsa} do not update 3600 * 1000")
    #     raise PreventUpdate
    # elif (tsa is not None) and (athlete is not None) and (graph is None): 
    #     # it athlete is known and the data is None, start the interval
    #     app.server.logger.info(f"stop_interval_data tsa:{tsa} athlete: {athlete}, start: 1000")
    #     return 2000
    # else:
    #     # other cases
    #     app.server.logger.info(f"stop_interval_data tsa:{tsa} athlete: {athlete} stop: 3600*100")
    #     return 3600*5000

@app.callback(Output('request', 'data'),
            [Input('graph', 'value'),
             Input('athlete', 'modified_timestamp')],
            [State('request', 'data')])
def increment_request(graph, tsa, r):
    if (tsa is None) or (graph is not None):
        app.server.logger.info(f"increment_request: tsa: {tsa} Do not update")
        raise PreventUpdate
    if r is None:
        app.server.logger.info(f"increment_request: tsa: {tsa} 0")
        return 0
    else:
        app.server.logger.info(f"increment_request: tsa: {tsa} {r+1}")
        return r+1


@app.callback(Output('graph', 'value'),
            [Input('request', 'modified_timestamp')],
            [State('athlete', 'data')])
def fetch_graph(tsr, athlete):
    """Generate graph"""
    if athlete:
        a = json.loads(athlete)
        _id = a.get('id', None)
    else:
        raise PreventUpdate

    r = requests.get('http://api:5042/data', params={'id': _id})
    _d = json.loads(r.text)
    app.server.logger.info(f"fetch_graph {len(_d)}")
    if len(_d) == 0:
        return None
    else: 
        d = process_data(_d)
        rv = plot_poster(d, a)
        return rv
    

    # _d = json.loads(r.text)
    # if len(_d) == 0:
    #     return None
    # else:
    #     d = process_data(_d)
    #     # rv = plot_poster(d, a)
    #     rv = "{abc}"
    #     app.server.logger.info(f"fetch_graph interval: {n_intervals}, Updata graph")
    # app.server.logger.info(f"fetch_graph interval: {n_intervals}, len(d): {len(_d)}")
    # return rv


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
        raise PreventUpdate
    return rv


if __name__ == '__main__':

    app.run_server(debug=True)
