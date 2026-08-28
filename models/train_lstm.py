import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.lstm_model import WeatherLSTM
from models.data_loader import WeatherDataset

# ===== 配置 =====
DATA_PATH = "data/beijing_weather.csv"
FEATURE_COLS = ['temperature', 'humidity', 'dni', 'wind_speed']
TARGET_COL = 'temperature'
SEQ_LEN = 7
HIDDEN_SIZE = 64
NUM_LAYERS = 2
EPOCHS = 50
BATCH_SIZE = 64
LR = 0.001

# ===== 加载数据 =====
df = pd.read_csv(DATA_PATH).sort_values('date')
print(f"总数据: {len(df)} 行")

# 按时间划分
train_size = int(0.7 * len(df))
val_size = int(0.15 * len(df))
train_df = df[:train_size]
val_df = df[train_size:train_size + val_size]
test_df = df[train_size + val_size:]

print(f"训练: {len(train_df)} 行, 验证: {len(val_df)} 行, 测试: {len(test_df)} 行")

# ===== 数据集 =====
train_dataset = WeatherDataset(train_df, FEATURE_COLS, TARGET_COL, SEQ_LEN)
val_dataset = WeatherDataset(val_df, FEATURE_COLS, TARGET_COL, SEQ_LEN)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

# ===== 模型 =====
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = WeatherLSTM(len(FEATURE_COLS), HIDDEN_SIZE, NUM_LAYERS).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LR)

# ===== 训练 =====
print("开始训练...")
best_val_loss = float('inf')
for epoch in range(EPOCHS):
    model.train()
    train_loss = 0
    for X, y in train_loader:
        X, y = X.to(device), y.to(device)
        optimizer.zero_grad()
        pred = model(X).squeeze()
        loss = criterion(pred, y)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()

    model.eval()
    val_loss = 0
    with torch.no_grad():
        for X, y in val_loader:
            X, y = X.to(device), y.to(device)
            pred = model(X).squeeze()
            val_loss += criterion(pred, y).item()

    if (epoch + 1) % 10 == 0:
        print(
            f"Epoch {epoch + 1}: Train Loss = {train_loss / len(train_loader):.4f}, Val Loss = {val_loss / len(val_loader):.4f}")

# ===== 保存模型 =====
os.makedirs("models", exist_ok=True)
torch.save(model.state_dict(), "models/lstm_weather.pth")
print("✅ 模型已保存到 models/lstm_weather.pth")

# 保存归一化参数
import pickle

with open("models/scaler.pkl", "wb") as f:
    pickle.dump((train_dataset.scaler_X, train_dataset.scaler_y), f)
print("✅ 归一化参数已保存")