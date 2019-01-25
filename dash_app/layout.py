import dash_core_components as dcc
import dash_html_components as html
from style import colors
from plots import jumbotron


def app_layout():
    """Returns app layout
    """
    rv = html.Div(
        id='app-layout',
        className = 'container-fluid no-gutters',
        children=[
            dcc.Location(id='url', refresh=False),
            dcc.Interval(id='interval-data', interval=1000, n_intervals=0),
            dcc.Store(id='athlete', storage_type='session'),
            dcc.Store(id='data', storage_type='session'),
            dcc.Store(id='graph', storage_type='session'),
            html.Div(id='none', style={'display': 'none'}),
            html.Div(id='page-content',
                className='row no-gutters',
                children=[
                    html.Div(make_left(), id='page-left', className='col-sm no-gutters'),
                    html.Div(make_right(), id='page-right', className='col-sm no-gutters')
                ]
            ),
        ]
    )
    return rv


def make_left(content=None):
    """Returns a div with a plot"""

    if content is None:
        rv = html.Div(children=[
                html.Div('Requires a powermeter data', className='alert alert-danger'),
                jumbotron()],
                className='no-gutters')
    else:
        rv=content
    return rv


def make_right(content=None):
    """Returns a div with a plot"""

    rv = html.Div(html.Img(src='/static/42_rides_velometria.jpg'),
        className='no-gutters')

    return rv

