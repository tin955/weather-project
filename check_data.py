import pandas as pd

df = pd.read_csv("D:/nasa_power/nasa_power_cleaned.csv")
print(f"行数: {len(df)}")
print(f"列名: {df.columns.tolist()}")
print(f"时间范围: {df['year'].min()} - {df['year'].max()}")
print(f"网格点数: {df.groupby(['latitude', 'longitude']).ngroups}")