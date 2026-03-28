import requests
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
from dotenv import load_dotenv
# from zhipuai import ZhipuAI #暂时注释，改用request方案，因为zhipuai库安装不了
load_dotenv()
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
GAODE_API_KEY = os.getenv("GAODE_API_KEY")
# 查看系统已安装的中文字体
fonts = [f.name for f in fm.fontManager.ttflist if 'Sim' in f.name or 'Kai' in f.name]
print("可用的中文字体：", fonts)

# 选一个可用的，比如 'SimHei', 'KaiTi', 'Microsoft YaHei'
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 微软雅黑
plt.rcParams['axes.unicode_minus'] = False



# 1. 调用API拉取数据
def fetch_weather_data(city):
    # 高德地图天气 API（需要你的 Key）
    # 注意：高德城市编码需要是中文城市名，如“北京”
    url = f"https://restapi.amap.com/v3/weather/weatherInfo?city={city}&key={GAODE_API_KEY}&output=JSON&extensions=base"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == '1' and data['infocode'] == '10000':
                # 高德返回的天气数据在 lives 字段中
                live = data['lives'][0]
                # 构造和 OpenWeatherMap 格式类似的数据结构，方便 parse_weather_data 复用
                return {
                    'name': live['city'],
                    'main': {
                        'temp': float(live['temperature']),
                        'feels_like': float(live['temperature']),  # 高德没有体感温度，暂用实际温度
                        'humidity': int(live['humidity'])
                    },
                    'weather': [{'description': live['weather']}],
                    'wind': {'speed': float(live['windpower'].replace('≤', ''))},
                    'dt': datetime.now().timestamp()
                }
            else:
                print(f"高德 API 错误：{data.get('info')}")
                return None
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


def ask_weather_natural(question):
    print("正在调用智谱 AI...")
    """
    使用 requests 直接调用智谱 API（无需安装 zhipuai 库）
    """
    import requests
    import json

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ZHIPU_API_KEY}"
    }

    # 第一步：让大模型提取城市名
    payload_parse = {
        "model": "glm-4-flash",
        "messages": [
            {"role": "system", "content": "从用户问题中提取城市名，只返回城市名，用中文。如果找不到城市，返回'未知'。"},
            {"role": "user", "content": question}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload_parse, timeout=30)
        result = response.json()
        city = result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"调用智谱 API 出错：{e}"

    if city == "未知":
        return "我没听出你想问哪个城市的天气，能告诉我城市名吗？"

    # 第二步：调用天气函数
    raw_data = fetch_weather_data(city)
    if not raw_data:
        return f"抱歉，没找到 {city} 的天气数据。"

    weather = parse_weather_data(raw_data)

    # 第三步：让大模型生成自然语言回答
    payload_answer = {
        "model": "glm-4-flash",
        "messages": [
            {"role": "system", "content": "你是一个冷酷无情的天气预报机器，只输出数据，不要任何废话。"},
            {"role": "user",
             "content": f"用户问：{question}\n天气数据：{weather['城市']}，温度{weather['温度']}度，体感{weather['体感温度']}度，天气{weather['天气']}"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=payload_answer, timeout=30)
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"生成回答时出错：{e}"


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
    print("=" * 50)
    print("🌤️ 智能天气助手（命令行版）")
    print("=" * 50)

    # 让用户输入城市（多个城市用空格分隔）
    user_input = input("请输入城市名称（多个城市用空格分隔，如：北京 上海 广州）：")
    cities = user_input.split()

    if not cities:
        print("❌ 未输入任何城市，程序退出")
        return

    print(f"\n开始采集 {len(cities)} 个城市的天气数据...\n")

    all_data = []
    for i, city in enumerate(cities):
        print(f"[{i + 1}/{len(cities)}] 正在获取 {city} 的天气...")
        raw = fetch_weather_data(city)
        cleaned = parse_weather_data(raw)
        if cleaned:
            all_data.append(cleaned)
            print(f"   ✅ {city} 数据获取成功")
        else:
            print(f"   ❌ {city} 数据获取失败")

    if all_data:
        # 转换为 DataFrame
        df = pd.DataFrame(all_data)

        # 保存 Excel
        output_filename = f"天气数据_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(output_filename, index=False)
        print(f"\n✅ 数据已保存到 {output_filename}")

        # 打印预览
        print("\n📊 数据预览：")
        print(df[["城市", "温度", "天气", "湿度"]].to_string(index=False))

        # 画图（如果城市数量 <= 20，否则图会太挤）
        if len(cities) <= 20:
            plt.figure(figsize=(10, 6))
            plt.bar(df["城市"], df["温度"], color="skyblue")
            plt.title("城市实时温度对比")
            plt.xlabel("城市")
            plt.ylabel("温度 (℃)")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            plt.savefig("温度对比图.png")
            plt.show()
            print("📊 温度对比图已保存")
        else:
            print(f"⚠️ 城市数量 {len(cities)} 超过 20，跳过图表生成")

        # AI 问答（对第一个城市）
        print("\n" + "=" * 50)
        print("🤖 智能问答演示")
        print("=" * 50)
        first_city = cities[0]
        question = f"{first_city}今天天气怎么样？"
        print(f"问：{question}")
        print("正在调用 AI 生成回答...")
        answer = ask_weather_natural(question)
        print(f"答：{answer}")

    else:
        print("\n❌ 未获取到任何城市的数据，请检查城市名称是否正确")

# 运行
if __name__ == "__main__":
    main()

