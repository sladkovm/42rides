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
            dcc.Interval(id='interval-data', interval=1000),
            html.Div(id='athlete', style={'display': 'none'}),
            html.Div(id='data', style={'display': 'none'}),
            html.Div(id='graph', style={'display': 'none'}),
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

    rv = html.Div(html.Img(src='/static/stravaio_poster_2018.jpg', width='100%'),
        className='no-gutters')

    return rv

