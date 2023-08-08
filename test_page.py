from dash import Dash, html, dcc, callback, Output, Input
from datetime import datetime, date
import plotly.express as px
import pandas as pd
# from preprocess_data import tweak_df_, get_temp_ranks
from callback_funcs import get_n_shapes_ranked
import os
from populate_data import populate_data

if 'scrubbed.csv' not in os.listdir():
    print('dataset not in current folder')
if 'tweaked.csv' not in os.listdir() or 'temp_ranks_df.csv' not in os.listdir():
    populate_data()
    print('populating data')


# # read in kaggle ufo dataset from local directory
# df = pd.read_csv('scrubbed.csv')
# # do first round of data processing
# tweaked = tweak_df_(df)
# tweaked.to_csv('tweaked.csv')
# # do processing for subsets to be used on specific graphs
# temp_ranks_df = get_temp_ranks(tweaked)
# temp_ranks_df.to_csv('temp_ranks_df.csv')


tweaked = pd.read_csv("tweaked.csv", index_col='datetime', parse_dates=True)
temp_ranks_df = pd.read_csv("temp_ranks_df.csv", index_col='datetime', parse_dates=True)

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1(
            children='Historical Shape Prevalence',
            style={'textAlign':'center'}
            )]),
    html.Div([
        dcc.Graph(id='graph-content')
        ]),
    html.Div([
        html.Div([
            html.Label(children='Number of Shapes', style={'textAlign':'center'}),
            dcc.Dropdown(list(range(2,11)), 5, id='n')],
            style={'textAlign':'center', 'display':'inline-block', 'width':'15%'}),
        html.Div([
            html.Label(children='Select Year Range'),
            dcc.RangeSlider(1906, 2014, 
                id='year-slider',
                marks={i:'{}'.format(str(i)) for i in range(1906, 2015, 5)},
                value=[1995,2014],
                tooltip={"placement":"bottom", "always_visible":True},
                pushable=5
                )],
            style={'display':'inline-block', 'width':'80%', 'textAlign':'center'}
                )], style={'textAlign':'center'}),
    
    html.Div([
        dcc.Dropdown(list(range(0,10)), 5, id='temp')
        ])
    ])

@callback(
    Output(component_id='graph-content', component_property='figure'),
    Input(component_id='n', component_property='value'),
    [Input(component_id='year-slider', component_property='value')]
    )
def update_graph(n, year_range):
    ranked_df = get_n_shapes_ranked(temp_ranks_df, n=n)
    ranked_subset = ranked_df.loc[str(year_range[0]):str(year_range[1])]
    fig = px.line(
        ranked_subset, x=ranked_subset.index.year, y='shape_rank',
        color='shape', markers=True
        )
    fig.update_yaxes(
        autorange='reversed',
        title_text='Shape Rank',
        tickmode='linear',
        dtick=1,
        tick0=0
        )
    fig.update_xaxes(title_text='Year')

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)