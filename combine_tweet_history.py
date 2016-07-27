# Combine all historical tweets from 2016 into a single csv

import pandas as pd
import os

file_list = []
bridge_data = pd.DataFrame()
for file in os.listdir(os.getcwd()):
    if "2016.csv" in file: 
        df = pd.read_csv(file)
        bridge_data = bridge_data.append(df)
        file_list.append(df)
        
bridge_data = bridge_data.drop_duplicates()

bridge_data.to_csv('bridge_records.csv')