import streamlit as st
import pandas as pd
import plotly.express as px

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"

st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 1 - 시간")
st.caption("KOBIS 일별 박스오피스 10위권 데이터를 시간의 흐름에 따라 살펴봅니다.")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 날짜(YYYYMMDD)를 실제 날짜형으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"].astype(str), format="%Y%m%d")

    # 숫자 열을 숫자형으로 변환
    numeric_columns = ["순위", "영화코드", "일관객", "누적관객", "스크린수", "상영횟수"]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.sort_values(["날짜", "순위"]).reset_index(drop=True)


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.caption(f"오류 내용: {e}")
    st.stop()


# ============================================================
# 그래프 1
# ============================================================
st.header("그래프 1. 영화별 일관객 변화")

movie_list = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_list,
)

movie_df = (
    df[df["영화명"] == selected_movie]
    .sort_values("날짜")
    [["날짜", "일관객"]]
    .copy()
)

fig = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie} — 날짜별 일관객",
    labels={
        "날짜": "날짜",
        "일관객": "일관객",
    },
)

fig.update_traces(
    hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
)

fig.update_layout(
    hovermode="x unified",
    xaxis=dict(
        tickformat="%Y-%m-%d",
        hoverformat="%Y-%m-%d",
    ),
    yaxis=dict(
        tickformat=",",
        separatethousands=True,
    ),
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("**이 그래프로 알 수 있는 것**")
st.empty()

st.divider()


# ============================================================
# 앞으로 추가할 그래프 영역
# ============================================================
st.header("그래프 2")
st.info("앞으로 추가할 그래프를 이 구역에 넣습니다.")

st.divider()

st.header("그래프 3")
st.info("앞으로 추가할 그래프를 이 구역에 넣습니다.")
