from preprocess_data import tweak_df_, get_temp_ranks, fetch_map_data
import pandas as pd
import os

def populate():
    """creates and cleans main dataset and creates other static dataframes to be used for 
    calculations by callback functions"""

    # read in kaggle ufo dataset from local directory
    if 'scrubbed.csv' not in os.listdir():
        raise Exception("dataset not in current folder")

    # format and store main dataset for further processing
    if 'tweaked.csv' not in os.listdir():
        df = pd.read_csv('scrubbed.csv')
        tweaked = tweak_df_(df)
        tweaked.to_csv('tweaked.csv')
    
    # create and store temp_ranks_df
    if 'temp_ranks_df.csv' not in os.listdir():
        tweaked = pd.read_csv("tweaked.csv", index_col='datetime', parse_dates=True,
            dtype={'shape':'category'})
        temp_ranks_df = get_temp_ranks(tweaked)
        temp_ranks_df.to_csv('temp_ranks_df.csv')

    # create and store location_raw df 
    if 'location_raw.csv' not in os.listdir():
        tweaked = pd.read_csv("tweaked.csv", index_col='datetime', parse_dates=True,
            dtype={'shape':'category'})
        print("\nAbout to make ~65000 api calls to " 
            "an FCC api that is not extremely fast. "
            "This program will print 'Done " 
            "making api calls' when finished")
        location_raw = fetch_map_data(tweaked)
        print('\nDone making api calls')
        location_raw.to_csv('location_raw.csv')

    # read counties.json from internet, store it as a json object
    # (and possibly also a dataframe)



    # populate the counties dataframe and store it as a csv 



        
    print('\nAll data is populated\n')
    
