import requests
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 查看系统已安装的中文字体
fonts = [f.name for f in fm.fontManager.ttflist if 'Sim' in f.name or 'Kai' in f.name]
print("可用的中文字体：", fonts)

# 选一个可用的，比如 'SimHei', 'KaiTi', 'Microsoft YaHei'
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 微软雅黑
plt.rcParams['axes.unicode_minus'] = False

import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")

# 1. 调用API拉取数据
def fetch_weather_data(city):

    # API接口（这里用一个免费公开的示例API）
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"

    try:
        # 发送GET请求
        response = requests.get(url)

        # 检查是否成功
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"请求失败，状态码：{response.status_code}")
            return None

    except Exception as e:
        print(f"发生错误：{e}")
        return None


# 2. 数据解析整理
def parse_weather_data(raw_data):
    if not raw_data:
        return None

    # 提取需要的信息
    parsed = {
        '城市': raw_data.get('name'),
        '温度': raw_data['main']['temp'],
        '体感温度': raw_data['main']['feels_like'],
        '湿度': raw_data['main']['humidity'],
        '天气': raw_data['weather'][0]['description'],
        '风速': raw_data['wind']['speed'],
        '时间戳': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return parsed


# 3. 保存到Excel
def save_to_excel(data, filename="weather_data.xlsx"):
    if not data:
        return

    # 转换为DataFrame
    df = pd.DataFrame([data])

    # 保存到Excel
    df.to_excel(filename, index=False)
    print(f"数据已保存到 {filename}")

    # 显示前几行
    print("\n数据预览：")
    print(df.head())


# 4. 主程序
def main():
    print("开始拉取数据...")

    #要采集的城市数据
    cities = ["Beijing", "Shanghai", "Guangzhou", "Chengdu", "Xi'an"]
    all_data = []
    #循环采集
    for city in cities:
        raw = fetch_weather_data(city)
        cleaned = parse_weather_data(raw)
        if cleaned:
            all_data.append(cleaned)

    if all_data:  # 确保至少有一个城市的数据


        # 将包含多个城市数据的列表，转换为 DataFrame
        df = pd.DataFrame(all_data)


        # 保存所有数据到一个新的 Excel 文件
        output_filename = "多城市天气对比.xlsx"
        df.to_excel(output_filename, index=False)
        print(f"\n 数据拉取完成！已保存所有城市数据到 {output_filename}")
        print("\n数据预览：")
        print(df[["城市", "温度", "天气"]])  # 只打印关键列，更清晰

        # 画图
        plt.figure(figsize=(10, 6))
        plt.bar(df["城市"], df["温度"], color="skyblue")
        plt.title("城市实时温度对比")
        plt.xlabel("城市")
        plt.ylabel("温度 (℃)")
        plt.savefig("温度对比图.png")  # 保存图片
        plt.show()
        print("温度对比图已保存")

    else:
        print("未获取到任何城市的数据")



# 运行
if __name__ == "__main__":
    main()
