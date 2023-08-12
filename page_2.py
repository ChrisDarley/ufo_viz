from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from callback_funcs  import get_n_shapes_ranked
from populate_data import populate
from graphing_funcs import update_graph_2
from functools import partial
import os

populate()

location_raw = pd.read_csv(
    'location_raw.csv', index_col='datetime',
    parse_dates=True, dtype={'County.FIPS':str}
    )

############################################

county_fips = pd.read_csv("county_fips.csv")

#########################################

population_path = os.path.join(
    os.getcwd(),
    'pop_data/nhgis0002_csv/nhgis0002_ts_nominal_county.csv'
    )

population_df = pd.read_csv(
    population_path,
    dtype={'STATEFP':str, 'COUNTYFP':str})

pop_fips = (population_df
    # selecing rows that have both county and state codes present
    .loc[lambda df_: 
        (~df_['STATEFP'].isna()) & 
        (~df_['COUNTYFP'].isna())]
    # combining the codes into one fips code
    .assign(fips=lambda df_:
        df_['STATEFP']+df_['COUNTYFP'])
    # dropping District of Columbia(11) and Puerto Rico(72)
    .loc[lambda df_:
        ~df_['STATEFP'].isin(['11', '72'])]
    )

pop_fips_set = set(pop_fips['fips'])

############################################

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1(
            children='Historical Map of UFO Sightings by County',
            style={'textAlign':'center'}
        )
    ]),
    html.Div([
        html.Label(children='Country')
    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)