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
