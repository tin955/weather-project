import requests
import os
from dotenv import load_dotenv

load_dotenv()
HFAK_API_KEY = os.getenv("HFAK_API_KEY")

# 北京的地区代码（你需要从文档里查到实际的代码）
# 华风爱科通常用数字代码，比如北京可能是 101010100
CITY_CODE = "101010100"  # 你先换成文档里查到的北京代码

url = "https://api.weathercn.com/v1/current"
params = {
    "location": CITY_CODE,
    "key": HFAK_API_KEY
}

print(f"正在查询北京天气，城市代码: {CITY_CODE}")
print(f"API Key: {HFAK_API_KEY[:10]}...")

response = requests.get(url, params=params, timeout=10)

print(f"状态码: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print("\n返回数据:")
    print(data)
else:
    print(f"错误信息: {response.text}")