import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import torch
from torch.utils.data import Dataset, DataLoader

# 读取数据
df = pd.read_csv("D:/nasa_power/nasa_power_cleaned.csv")
print(f"总数据: {len(df)} 行")

# 选北京附近的网格点 (39.5-40.5°N, 116.0-117.0°E)
beijing = df[(df['latitude'].between(39.5, 40.5)) &
             (df['longitude'].between(116.0, 117.0))].copy()
beijing = beijing.sort_values(['year', 'doy'])
print(f"北京数据: {len(beijing)} 行")

# 构造日期列
beijing['date'] = pd.to_datetime(beijing[['year', 'month']].assign(day=1))

# 选择特征
feature_cols = ['temperature', 'humidity', 'dni', 'wind_speed']
target_col = 'temperature'

# 保存原始数据（用于反归一化）
beijing.to_csv("data/beijing_weather.csv", index=False)
print("✅ 已保存 data/beijing_weather.csv")