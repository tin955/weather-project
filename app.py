import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from city_weather import fetch_weather_data, parse_weather_data, ask_weather_natural
from rag.retriever import retrieve_context
from models.predict import predict_next_days
import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()
client = ZhipuAI(api_key=os.getenv("ZHIPU_API_KEY"))

# 页面设置
st.set_page_config(
    page_title="智能天气助手",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ 智能天气助手")
st.markdown("输入城市名称，获取实时天气 + AI 暖心回答")

# ========== 侧边栏导航 ==========
mode = st.sidebar.radio(
    "选择功能",
    ["🌤️ 实时天气", "🔮 温度预测", "📚 知识库问答"]
)

# ============================================================
# 模式1：实时天气
# ============================================================
if mode == "🌤️ 实时天气":
    with st.sidebar:
        st.header("🔍 查询设置")
        city_input = st.text_input(
            "城市/区的名称（多个城市用空格分隔）",
            value="北京 朝阳区",
            help="例如：北京 上海 深圳 杭州"
        )
        query_button = st.button("🚀 开始查询", type="primary")
        st.markdown("---")
        st.caption("💡 提示：支持任意城市，如「南宁」「乌鲁木齐」「东京」")

    if query_button:
        cities = city_input.split()
        if not cities:
            st.warning("请输入至少一个城市")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            all_data = []
            for i, city in enumerate(cities):
                status_text.text(f"正在获取 {city} 的天气...")
                raw = fetch_weather_data(city)
                cleaned = parse_weather_data(raw)
                if cleaned:
                    all_data.append(cleaned)
                progress_bar.progress((i + 1) / len(cities))
            status_text.text("✅ 数据采集完成！")

            if all_data:
                df = pd.DataFrame(all_data)
                st.subheader("📊 实时天气数据")
                st.dataframe(df[["城市", "温度", "体感温度", "湿度", "天气", "风速"]], use_container_width=True, hide_index=True)

                if len(cities) <= 20:
                    st.subheader("📈 温度对比图")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.bar(df["城市"], df["温度"], color="skyblue")
                    ax.set_title("城市实时温度对比", fontsize=14)
                    ax.set_xlabel("城市")
                    ax.set_ylabel("温度 (℃)")
                    ax.set_ylim(0, max(df["温度"]) + 5)
                    plt.xticks(rotation=45, ha='right')
                    plt.tight_layout()
                    st.pyplot(fig)

                # 导出 Excel
                df.to_excel("temp_weather.xlsx", index=False)
                with open("temp_weather.xlsx", "rb") as f:
                    st.download_button(
                        label="📥 下载 Excel 文件",
                        data=f,
                        file_name=f"天气数据_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

                st.subheader("🤖 AI 天气助手")
                with st.spinner("AI 正在思考中..."):
                    first_city = cities[0]
                    question = f"{first_city}今天天气怎么样？"
                    answer = ask_weather_natural(question)
                st.info(f"**问：{question}**\n\n答：{answer}")
            else:
                st.error("❌ 未获取到任何天气数据，请检查城市名称是否正确")

# ============================================================
# 模式2：温度预测
# ============================================================
elif mode == "🔮 温度预测":
    st.header("🔮 未来3天温度预测")
    st.caption("基于 2015-2024 年气象数据 LSTM 模型，支持区级预测")

    # 让用户输入区域
    district = st.text_input("输入区级地名（如：海淀区、朝阳区）", "海淀区")

    if st.button("开始预测"):
        with st.spinner("模型推理中..."):
            try:
                # 1. 获取该区的经纬度
                from city_weather import get_location
                lat, lng = get_location(district)
                if lat is None:
                    st.error(f"未找到 {district} 的经纬度，请检查输入")
                else:
                    # 2. 从 NASA 数据中提取该网格点
                    import pandas as pd
                    df = pd.read_csv("D:/nasa_power/nasa_power_cleaned.csv")

                    # 找最近的网格点
                    df['dist'] = ((df['latitude'] - lat)**2 + (df['longitude'] - lng)**2)**0.5
                    nearest = df.loc[df['dist'].idxmin()]

                    st.info(f"📍 匹配到网格点: {nearest['latitude']:.2f}°N, {nearest['longitude']:.2f}°E")

                    # 提取该网格点的历史数据
                    grid_df = df[(df['latitude'] == nearest['latitude']) &
                                 (df['longitude'] == nearest['longitude'])].copy()
                    grid_df = grid_df.sort_values(['year', 'doy'])
                    grid_df['date'] = pd.to_datetime(grid_df[['year', 'month']].assign(day=1))

                    # 3. 用 LSTM 模型预测
                    from models.predict import predict_next_days
                    preds = predict_next_days(grid_df, days=3)

                    col1, col2, col3 = st.columns(3)
                    col1.metric("第 1 天", f"{preds[0]} °C")
                    col2.metric("第 2 天", f"{preds[1]} °C")
                    col3.metric("第 3 天", f"{preds[2]} °C")

                    # 显示该地区历史温度范围
                    temp_min = grid_df['temperature'].min()
                    temp_max = grid_df['temperature'].max()
                    st.caption(f"📊 该地区历史温度范围: {temp_min:.1f}°C ~ {temp_max:.1f}°C")

            except Exception as e:
                st.error(f"预测失败: {e}")

# ============================================================
# 模式3：知识库问答
# ============================================================
elif mode == "📚 知识库问答":
    st.header("📚 知识库问答")
    st.caption("可回答 CSP、新能源、气象政策等相关问题")
    question = st.text_input("请输入你的问题")
    if st.button("提问") and question:
        with st.spinner("检索中..."):
            try:
                contexts = retrieve_context(question)
                context_text = "\n".join(contexts)
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[
                        {"role": "system", "content": f"根据以下资料回答问题：\n{context_text}"},
                        {"role": "user", "content": question}
                    ]
                )
                answer = response.choices[0].message.content
                st.markdown("### 📝 回答")
                st.write(answer)
                with st.expander("📖 引用来源"):
                    for ctx in contexts:
                        st.write(f"- {ctx[:200]}...")
            except Exception as e:
                st.error(f"检索失败: {e}")