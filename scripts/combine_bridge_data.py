# Combine all historical tweets from 2016 into a single csv

import pandas as pd
import os

bridge_data_dir = '../data/bridge'
file_list = []
bridge_data = pd.DataFrame()
for file in os.listdir(bridge_data_dir):
    if "2016.csv" in file: 
        df = pd.read_csv(bridge_data_dir + r'/' + file)
        bridge_data = bridge_data.append(df)
        file_list.append(df)
        
bridge_data = bridge_data.drop_duplicates()

bridge_data.to_csv(bridge_data_dir + r'/bridge_records.csv')