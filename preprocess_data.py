import pandas as pd
import numpy as np
import requests

def tweak_df_(df):
    """function to clean the dataset and make adjustments for plotting"""
    return (df
    # splitting datetime into day and hour columns
    .join(other=df
        .datetime.str.split(' ', expand=True)
        .rename(columns={0:'day',1:'hour'})
        .astype({'day': 'datetime64[ns]'}))
    # changing hour and day when hour is at 24:00
    .assign(day=lambda df_: df_['day'].where(~(df_['hour']=='24:00'), df_.day+pd.Timedelta(1,'day')))
    .replace({'hour':'24:00'},'00:00')
    # Combining day and hour back into new datetime column
    .assign(datetime=lambda df_:pd.to_datetime(df_.day.astype(str)+' '+df_.hour))
    # Set the datetime column as the index and sort df entries by date
    .set_index('datetime')
    .sort_index()
    # creating comment_length column
    .astype({'comments':'string'})
    .assign(
        comment_list=lambda df_: df_.comments.str.split(' '),
        comment_length=lambda df_: 
            df_.comment_list.apply(lambda x: (len(x) if isinstance(x, list) else x)))
    # converting columns categorical or numeric dtypes
    .assign(
        duration_seconds = lambda df_: pd.to_numeric(df_["duration (seconds)"], errors='coerce'),
        latitude=lambda df_: pd.to_numeric(df_["latitude"], errors='coerce'),
        longitude=lambda df_: pd.to_numeric(df_["longitude "], errors='coerce'),
        country=lambda df_: pd.Categorical(df_["country"]),
        shape=lambda df_: pd.Categorical(df_["shape"]),
        comment_length=lambda df_: pd.to_numeric(df_["comment_length"], errors='coerce'))
    # dropping all durations longer than 1 hour (3600 seconds)
    .assign(duration_seconds=lambda df_: df_["duration_seconds"].where(
        df_["duration_seconds"]<3600, np.nan))
    # coercing uncommon shape names into more common categories and changing dtype to category
    .assign(shape=lambda df_: df_['shape'].replace({
        'changed':'changing', 'crescent':'other', 'delta':'triangle',
        'dome':'circle', 'flare':'light', 'hexagon':'other', 
        'pyramid':'triangle', 'round':'circle'}))
    .astype({'shape':'category'})
    # dropping unnecessary columns
    .drop(columns=["day", "hour", "duration (seconds)", "duration (hours/min)",
            "date posted", "longitude ", "comment_list", "comments"])
    )

def get_temp_ranks(tweaked_):
    """function to return a temporary dataframe to serve as a base for 
    get_n_shapes_ranked callback function"""
    return (tweaked_
        .assign(counts=lambda df_: 
            df_.groupby([df_.index.year, 'shape'])
            .shape
            .transform('count'))
        .assign(year=lambda df_: df_.index.year)
        .drop_duplicates(
            subset=['year', 'shape', 'counts'],
            keep='first')
        .assign(temp_rank= lambda df_:
            df_.groupby(df_.index.year)
                .counts
                .transform('rank', method='first')))[
        ['year', 'counts', 'temp_rank', 'shape']]

def fetch_map_data(tweaked_):
    """Fetch United States geographical data from FCC and 
    transform into dataframe for further processing"""

    def get_request(query_string):
        """fetch data from fcc api for a given query string"""
        r = requests.get(query_string)
        if r.status_code == 200:
            return r.json()
        else:
            return {"row":"ignore"}
    
    def create_schema(df_):
        global new_cols_df
        new_cols_df = (
            pd.json_normalize(
                df_["selected_json"].to_list())
            .set_index(df_.index))
        return df_
    
    return (tweaked_
        # select rows where country is 'us' and lat and lon are not null
        .loc[lambda df_: 
            (df_["country"]=='us')&
            (~df_["latitude"].isna())&
            (~df_["longitude"].isna())    
            ]
        .assign(
            # make a query string for every row based on latitude and
            # longitude and add it to a column
            query_string=lambda df_: df_.apply(lambda row:
                f"https://geo.fcc.gov/api/census/block/find?latitude="
                f"{row['latitude']}%09&longitude={row['longitude']}&c"
                f"ensusYear=2020&showall=false&format=json", axis=1),
            # make an api call for each query string and store
            # the resulting json in the json column
            json=lambda df_: df_["query_string"].apply(func=get_request),
            # select the key value pairs from the json column that I care
            # about
            selected_json = lambda df_: df_["json"].apply(
                lambda row: {k:v for k,v in row.items() if 
                    k in ['County', 'State', 'Block', 'status']})
            )
        # create a global variable called 'new_cols_df' and use it to
        # store a dataframe constructed using the selected json values
        .pipe(create_schema)
        # join the current dataframe with the new_cols_df dataframe
        .join(new_cols_df)
        )
    