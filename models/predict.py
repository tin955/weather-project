import torch
import pandas as pd
import numpy as np
import pickle
import os
import sys
from models.lstm_model import WeatherLSTM
sys.path.append(".")


def load_model(model_path="models/lstm_weather.pth", scaler_path="models/scaler.pkl"):
    # 加载模型
    model = WeatherLSTM(input_size=4, hidden_size=64, num_layers=2)
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()

    # 加载归一化参数
    with open(scaler_path, "rb") as f:
        scaler_X, scaler_y = pickle.load(f)

    return model, scaler_X, scaler_y


def predict_next_days(df, days=3, seq_len=7):
    """预测未来 days 天的温度"""
    model, scaler_X, scaler_y = load_model()

    feature_cols = ['temperature', 'humidity', 'dni', 'wind_speed']

    # 取最后 seq_len 天的数据
    last_seq = df[feature_cols].values[-seq_len:]
    last_seq_scaled = scaler_X.transform(last_seq)
    current_seq = last_seq_scaled.copy()

    predictions = []
    for _ in range(days):
        input_tensor = torch.FloatTensor(current_seq).unsqueeze(0)
        with torch.no_grad():
            pred_scaled = model(input_tensor).item()
        pred = scaler_y.inverse_transform([[pred_scaled]])[0][0]
        predictions.append(round(pred, 1))

        # 滚动更新序列
        new_step = current_seq[-1].copy()
        new_step[0] = pred_scaled  # temperature 列用预测值
        current_seq = np.vstack([current_seq[1:], new_step])

    return predictions


if __name__ == "__main__":
    df = pd.read_csv("data/beijing_weather.csv").sort_values('date')
    preds = predict_next_days(df, days=3)
    print(f"未来3天温度预测: {preds} °C")