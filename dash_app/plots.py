import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
import numpy as np
from style import colors


# define data declaratively as a dict
bar_plot=dcc.Graph(id='fig',
            figure={
                'data':[{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                    {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},],
                'layout': {'title': "Bar Plot"}
                })

scatter_plot=dcc.Graph(id='fig',
            figure={
              'data': [
                    go.Scatter({
                        'name': 'Sin(x)',
                        'x': np.arange(10),
                        'y': np.sin(np.arange(10))
                    })
                ],
                'layout': {'title': 'Scatter Plot'}  
            })



def jumbotron():

    rv = html.Div(
                    children = [
                        
                        html.Br(),
                        html.Br(),
                        html.H1('42 Strava Rides', className='display-4'),
                        html.Br(),
                        html.P('Generate a poster with recent 42 Strava Rides', className='lead'),
                        html.P('Marvel at suffering done above and below FTP', className='lead'),
                        html.P('Relive the 1 sec, 1 min, 5 min and 20 min PRs', className='lead'),
                        html.A('Connect with Strava',
                            href='http://strava.com',
                            className='btn btn-danger btn-lg'),
                    ],
                    className = 'jumbotron',
                    style={
                        'background-color':'transparent'
                    })

    return rv
