from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
from callback_funcs  import get_n_shapes_ranked
from populate_data import populate
from graphing_funcs import update_graph_2
from functools import partial

populate()

tweaked = pd.read_csv("tweaked.csv", index_col='datetime', parse_dates=True,
    dtype={'shape':'category'})
temp_ranks_df = pd.read_csv("temp_ranks_df.csv", index_col='datetime',
    parse_dates=True, dtype={'shape':'category'})
# location_raw=pd.read_csv("location_raw.csv")

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1(
            children='Historical Prevalence of UFO Sighting Shapes',
            style={'textAlign':'center'}
            )]),
    html.Div([
        dcc.Graph(id='graph-2-content'),
        html.Div([
            html.Label(children='Country'),
            dcc.Dropdown(options=[
                {'label':'All Countries', 'value':'all'},
                {'label':'United States', 'value':'us'},
                {'label':'Canada', 'value':'ca'},
                {'label':'Great Britain', 'value':'gb'},
                {'label':'Australia', 'value':'au'},
                {'label':'Denmark', 'value':'de'}
            ],
            value='all',
            id='country')],
            # dcc.Dropdown(list(tweaked["country"].dropna().unique())+["all"],
            #     'all', id='country')],
            style={'width':'15%', 'marginLeft': '7%'})
    ]),
    html.Div([
        dcc.Graph(id='graph-1-content')
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
    # html.Div([
    #     dcc.Graph(id='graph-2-content'),
    #     dcc.Dropdown(list(tweaked["country"].dropna().unique())+["all"],
    #                 'all', id='country')
    #     ])
    ])

@callback(
    Output(component_id='graph-1-content', component_property='figure'),
    Input(component_id='n', component_property='value'),
    [Input(component_id='year-slider', component_property='value')]
    )
def update_graph_1(n, year_range):
    ranked_df = get_n_shapes_ranked(temp_ranks_df, n=n)
    ranked_subset = ranked_df.loc[str(year_range[0]):str(year_range[1])]
    fig = px.line(
        ranked_subset, x=ranked_subset.index.year, y='shape_rank',
        color='shape', markers=True, title='Rank of UFO Sighting Shapes by Year',
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

update_graph_2 = callback(
    Output(component_id='graph-2-content', component_property='figure'),
    Input(component_id='country', component_property='value')
    )(partial(update_graph_2, tweaked))

if __name__ == '__main__':
    app.run_server(debug=True)