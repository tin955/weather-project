import torch
from torch.utils.data import Dataset
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


class WeatherDataset(Dataset):
    def __init__(self, df, feature_cols, target_col, seq_len=7):
        self.seq_len = seq_len
        self.feature_cols = feature_cols
        self.target_col = target_col

        # 标准化
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()

        X = df[feature_cols].values
        y = df[target_col].values.reshape(-1, 1)

        X_scaled = self.scaler_X.fit_transform(X)
        y_scaled = self.scaler_y.fit_transform(y).flatten()

        # 构造序列样本
        self.X, self.y = [], []
        for i in range(len(df) - seq_len):
            self.X.append(X_scaled[i:i + seq_len])
            self.y.append(y_scaled[i + seq_len])

        self.X = torch.tensor(np.array(self.X), dtype=torch.float32)
        self.y = torch.tensor(np.array(self.y), dtype=torch.float32)

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

    def inverse_transform_y(self, y_scaled):
        return self.scaler_y.inverse_transform(y_scaled.reshape(-1, 1)).flatten()