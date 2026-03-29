# 智能天气助手

基于高德天气 API 和智谱大模型的天气问答系统。支持任意城市查询，自动生成数据报表和可视化图表，并提供 AI 自然语言问答。

---

## 功能

- 任意城市天气查询
- 自动生成 Excel 数据报表
- 温度对比柱状图
- AI 自然语言问答
- 网页交互界面

---

## 技术栈

- Python 3.12
- Streamlit
- 高德地图天气 API
- 智谱 GLM-4-Flash
- Pandas
- Matplotlib
- Git / GitHub

---

## 本地运行

1. 克隆仓库
   ```
   git clone https://github.com/tin955/weather-project.git
   cd weather-project
   ```

2. 安装依赖
   ```
   pip install -r requirements.txt
   ```

3. 配置环境变量
   创建 .env 文件，填入以下内容
   ```
   WEATHER_API_KEY=你的高德API Key
   ZHIPU_API_KEY=你的智谱API Key
   ```

4. 运行应用
   ```
   streamlit run app.py
   ```

浏览器打开 http://localhost:8501 即可使用。

---

## 项目结构

weather-project/
├── app.py
├── city_weather.py
├── requirements.txt
├── .env
└── README.md

---

## 环境变量

| 变量名 | 说明 | 获取方式 |
| --- | --- | --- |
| WEATHER_API_KEY | 高德天气 API Key | 高德开放平台 |
| ZHIPU_API_KEY | 智谱 AI API Key | 智谱开放平台 |

---

## 作者

tin955
