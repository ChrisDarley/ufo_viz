from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
# from preprocess_data import tweak_df_, get_temp_ranks
# from callback_funcs import get_n_shapes_ranked
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
    html.H1(children='Graph 1', style={'testAlign':'center'}),
    dcc.Dropdown(tweaked.country.dropna().unique(), 'us', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
])

@callback(
    Output(component_id='graph-content', component_property='figure'),
    Input(component_id='dropdown-selection', component_property='value')
)
def update_graph(value):
    dff = tweaked[tweaked.country==value]
    return px.scatter(dff, x=dff.index.year, y='comment_length')

if __name__ == '__main__':
    app.run_server(debug=True)