import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go
from plotly import tools
import numpy as np
import pandas as pd
import maya
from style import colors


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
                            href='http://test.velometria.com/api/authorize',
                            className='btn btn-danger btn-lg'),
                    ],
                    className = 'jumbotron',
                    style={
                        'background-color':'transparent'
                    })

    return rv


def process_data(raw_watts):
    to_plot = []
    power_old = [0,0,0,0]
    for d in raw_watts:
        d_plot = {}
        watts = pd.Series(list(d.values())[0])
        
        _power_max = power_max(watts)
        d_plot.update({'power_max': _power_max})
        
        _power_color = [power_color(pn, po) for pn, po in zip(_power_max, power_old)]
        d_plot.update({'power_color': _power_color})
        
        power_old = [pn if pn>po else po for pn, po in zip(_power_max, power_old)]
        
        _streams = pd.DataFrame()
        _streams['watts'] = watts
        _streams['watts_smooth'] = watts.rolling(10, min_periods=1).mean()
        
        _streams['time'] = pd.Series(np.arange(len(watts)))
        _streams['color'] = pd.Series(np.arange(len(watts)))
        _streams['color'].loc[watts>=250] = "#fc4c02"
        _streams['color'].loc[watts<250] = "#FFF"
        d_plot.update({'streams': _streams})
        
        d_plot.update({'date': maya.parse(list(d.keys())[0]).slang_date()})
        
        to_plot.append(d_plot)

    return to_plot


def power_max(watts):
    """Returns a list of Power Bests for the ride"""
    pm = [
        watts.rolling(5).mean().max(),
        watts.rolling(60).mean().max(),
        watts.rolling(5*60).mean().max(),
        watts.rolling(20*60).mean().max()
    ]
    rv = [int(p) if p is not np.NAN else 0 for p in pm]
    return rv


def power_color(new, old):
    """Return orange if the new values is a PR"""
    if new > old:
        return "#fc4c02"
    else:
        return "#FFF"


def plot_poster(to_plot):
    # n_plots = len(to_plot)
    MODE = 'markers'
    n_plots = 2
    specs = [[{}, {}, {}] for i in range(n_plots)]
    fig = tools.make_subplots(rows=n_plots, cols=3,
                              specs=specs,
                              shared_xaxes=True,
                              shared_yaxes=True,
                              vertical_spacing=0.0001)


    yaxis_settings = dict(showline=False, zeroline=False, showgrid=False,
                                                      showticklabels=False, zerolinewidth=0)
    xaxis_settings1 = dict(showline=False, zeroline=False, showgrid=False,
                                                      showticklabels=False,
                          domain=[0, 0.1])

    xaxis_settings2 = dict(showline=False, zeroline=False, showgrid=False,
                                                      showticklabels=True,
                        tickvals=[3600, 2*3600, 3*3600],
                        ticktext=['1h' ,'2h', '3h'],
                          domain=[0.1, 0.8])

    xaxis_settings3 = dict(showline=False, zeroline=False, showgrid=False,
                                                      showticklabels=True,
                          domain=[0.8, 1.0])

    _=1
    for d in to_plot:
        if _ < (n_plots+1):
            # Date and name
            trace = go.Bar({
                "x":[0],
                "y":[1],
                "text": [d['date']],
                "textposition": "outside",
                "textfont": {"color": "#FFF"},
                "marker": {"color": "#111",
                           "line": {
                               "width": 1,
                               "color": "#fc4c02"
                           }
                          }
            })
            fig.append_trace(trace, _, 1)

            # Scatter
            trace = go.Scattergl({
                "x": d['streams']['time'],
                "y": d['streams']['watts_smooth'],
                "mode": MODE,
                "marker": {"color": d['streams']['color'],
                           "size": 1},
                "textfont": {"color": "#FFF"},
            })
            fig.append_trace(trace, _, 2)

            # Bar
            trace = go.Bar({
                "x": ["5 sec", "1 min", "5 min", "20 min"],
                "y": [1,1,1,1],
                "text": d['power_max'],
                "textposition": "outside",
                "textfont": {"color": d['power_color']},
                "marker": {"color": '#111',
                           "line": {
                               "width": 1,
                               "color": "#fc4c02"
                           }
                          }
            })
            fig.append_trace(trace, _, 3)
            _+=1
            if _ > 1:
                fig['layout'].update({f'yaxis{2*_ - 1}': yaxis_settings})
                fig['layout'].update({f'yaxis{2*_-2}': yaxis_settings})
            else:
                fig['layout'].update({'yaxis': yaxis_settings})
                fig['layout'].update({'yaxis2': yaxis_settings})
        else:
            break

    fig['layout'].update(title='42 Strava Rides',
                         font=dict(family="Courier New", color="#FFF"),
                         height=800,
                         showlegend=False, paper_bgcolor='#111', plot_bgcolor='#111',
                         yaxis=yaxis_settings,
                         xaxis=xaxis_settings1,
                         xaxis2=xaxis_settings2,
                         xaxis3=xaxis_settings3)

    return fig
