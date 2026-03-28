import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from city_weather import fetch_weather_data, parse_weather_data, ask_weather_natural

# 页面设置
st.set_page_config(
    page_title="智能天气助手",
    page_icon="🌤️",
    layout="wide"
)

# 标题
st.title("🌤️ 智能天气助手")
st.markdown("输入城市名称，获取实时天气 + AI 暖心回答")

# 侧边栏输入
with st.sidebar:
    st.header("🔍 查询设置")
    city_input = st.text_input(
        "城市名称（多个城市用空格分隔）",
        value="北京 上海 广州",
        help="例如：北京 上海 深圳 杭州"
    )
    query_button = st.button("🚀 开始查询", type="primary")
    st.markdown("---")
    st.caption("💡 提示：支持任意城市，如「南宁」「乌鲁木齐」「东京」")

# 主界面
if query_button:
    cities = city_input.split()

    if not cities:
        st.warning("请输入至少一个城市")
    else:
        # 进度条
        progress_bar = st.progress(0)
        status_text = st.empty()

        # 采集数据
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

            # ========== 表格展示 ==========
            st.subheader("📊 实时天气数据")
            st.dataframe(
                df[["城市", "温度", "体感温度", "湿度", "天气", "风速"]],
                use_container_width=True,
                hide_index=True
            )

            # ========== 温度对比图 ==========
            if len(cities) <= 20:
                st.subheader("📈 温度对比图")
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(df["城市"], df["温度"], color="skyblue")
                ax.set_title("城市实时温度对比", fontsize=14)
                ax.set_xlabel("城市")
                ax.set_ylabel("温度 (℃)")
                ax.set_ylim(0, max(df["温度"]) + 5)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info(f"城市数量 {len(cities)} 超过 20，跳过图表生成")

            # ========== 导出 Excel ==========
            excel_buffer = pd.ExcelWriter("temp_weather.xlsx", engine="openpyxl")
            df.to_excel(excel_buffer, index=False)
            excel_buffer.close()
            with open("temp_weather.xlsx", "rb") as f:
                st.download_button(
                    label="📥 下载 Excel 文件",
                    data=f,
                    file_name=f"天气数据_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            # ========== AI 问答 ==========
            st.subheader("🤖 AI 天气助手")
            with st.spinner("AI 正在思考中..."):
                first_city = cities[0]
                question = f"{first_city}今天天气怎么样？"
                answer = ask_weather_natural(question)

            st.info(f"**问：{question}**\n\n答：{answer}")

            # 如果城市数量 > 1，还可以让用户选择其他城市提问
            if len(cities) > 1:
                st.markdown("---")
                st.caption("💬 试试问其他城市：")
                cols = st.columns(min(5, len(cities)))
                for idx, city in enumerate(cities):
                    if idx < len(cols):
                        with cols[idx]:
                            if st.button(f"问 {city}", key=f"btn_{city}"):
                                with st.spinner("AI 正在思考中..."):
                                    q = f"{city}今天天气怎么样？"
                                    a = ask_weather_natural(q)
                                st.success(f"**{city}**：{a}")
        else:
            st.error("❌ 未获取到任何天气数据，请检查城市名称是否正确")

# 页脚
st.markdown("---")
st.caption("Powered by 高德天气 API + 智谱 GLM-4-Flash | 数据实时更新")