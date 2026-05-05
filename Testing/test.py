import pandas as pd
df=pd.read_csv("data_source/Processed/processed_manufacturing.csv")
print(df.duplicated().sum())