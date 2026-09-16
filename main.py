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


@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(DATA_URL)

    # 열 이름의 앞뒤 공백과 BOM 제거
    df.columns = df.columns.astype(str).str.replace("\\ufeff", "", regex=False).str.strip()

    # 데이터에 따라 표기가 다른 경우를 대비
    column_aliases = {
        "상영횟상": "상영횟수",
        "상영횟수 ": "상영횟수",
    }
    df = df.rename(columns=column_aliases)

    required_columns = ["날짜", "순위", "영화코드", "영화명", "일관객", "누적관객", "스크린수"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"필요한 열이 없습니다: {', '.join(missing)}")

    # 날짜를 실제 날짜형으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str).str.strip(),
        format="%Y%m%d",
        errors="coerce",
    )

    # 숫자 열을 숫자형으로 변환
    for col in ["순위", "영화코드", "일관객", "누적관객", "스크린수"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 그래프에 필요한 행만 남김
    df = df.dropna(subset=["날짜", "영화명", "일관객"])

    return df.sort_values(["날짜", "순위"]).reset_index(drop=True)


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.code(str(e))
    st.stop()


# ============================================================
# 그래프 1
# ============================================================
st.header("그래프 1. 영화별 일관객 변화")

movie_list = sorted(df["영화명"].unique())

if movie_list:
    selected_movie = st.selectbox("영화를 선택하세요.", movie_list)

    movie_df = (
        df[df["영화명"] == selected_movie]
        .sort_values("날짜")[["날짜", "일관객"]]
    )

    fig = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        markers=True,
        title=f"{selected_movie} — 날짜별 일관객",
        labels={"날짜": "날짜", "일관객": "일관객"},
    )

    fig.update_traces(
        hovertemplate="날짜: %{x|%Y-%m-%d}<br>일관객: %{y:,}명<extra></extra>"
    )
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(tickformat="%Y-%m-%d"),
        yaxis=dict(tickformat=",", separatethousands=True),
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**이 그래프로 알 수 있는 것**")
    st.empty()
else:
    st.warning("표시할 영화 데이터가 없습니다.")

st.divider()


# ============================================================
# 그래프 2
# ============================================================
st.header("그래프 2. 일관객 합계 TOP 5 영화의 날짜별 변화")

top5_movies = (
    df.groupby("영화명")["일관객"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index
    .tolist()
)

top5_df = (
    df[df["영화명"].isin(top5_movies)]
    .groupby(["날짜", "영화명"], as_index=False)["일관객"]
    .sum()
    .sort_values(["날짜", "영화명"])
)

fig_top5 = px.line(
    top5_df,
    x="날짜",
    y="일관객",
    color="영화명",
    markers=True,
    title="일관객 합계 TOP 5 영화 — 날짜별 일관객",
    labels={"날짜": "날짜", "일관객": "일관객", "영화명": "영화"},
)

fig_top5.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "일관객: %{y:,}명<extra>%{fullData.name}</extra>"
    )
)
fig_top5.update_layout(
    hovermode="x unified",
    xaxis=dict(tickformat="%Y-%m-%d"),
    yaxis=dict(tickformat=",", separatethousands=True),
    legend=dict(title="영화", itemclick="toggle", itemdoubleclick="toggleothers"),
)

st.plotly_chart(fig_top5, use_container_width=True)
st.markdown("**이 그래프로 알 수 있는 것**")
st.empty()
st.divider()


# ============================================================
# 그래프 3
# ============================================================
st.header("그래프 3. 날짜별 10위권 일관객 합계")

daily_total = (
    df.groupby("날짜", as_index=False)["일관객"]
    .sum()
    .sort_values("날짜")
)

top3_days = daily_total.nlargest(3, "일관객")

fig_daily = px.area(
    daily_total,
    x="날짜",
    y="일관객",
    title="날짜별 10위권 일관객 합계",
    labels={"날짜": "날짜", "일관객": "10위권 일관객 합계"},
)

fig_daily.update_traces(
    hovertemplate=(
        "날짜: %{x|%Y-%m-%d}<br>"
        "10위권 일관객 합계: %{y:,}명<extra></extra>"
    )
)

for _, row in top3_days.iterrows():
    fig_daily.add_annotation(
        x=row["날짜"],
        y=row["일관객"],
        text=row["날짜"].strftime("%Y-%m-%d"),
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-45,
        font=dict(size=12),
    )

fig_daily.update_layout(
    hovermode="x unified",
    xaxis=dict(tickformat="%Y-%m-%d"),
    yaxis=dict(tickformat=",", separatethousands=True),
)

st.plotly_chart(fig_daily, use_container_width=True)
st.markdown("**이 그래프로 알 수 있는 것**")
st.empty()
st.divider()


# ============================================================
# 그래프 4
# ============================================================
st.header("그래프 4. 영화별 기간 일관객 TOP 10")

# 영화별 기간 일관객 합계와 10위권에 든 날짜 수를 계산
top10_movies = (
    df.groupby("영화명")
    .agg(
        일관객합계=("일관객", "sum"),
        일관객10위권일수=("날짜", "nunique"),
    )
    .sort_values("일관객합계", ascending=False)
    .head(10)
    .reset_index()
)

# 가로 막대그래프에서 큰 값이 위에 오도록 내림차순 기준으로 설정
top10_movies = top10_movies.sort_values("일관객합계", ascending=True)

fig_top10 = px.bar(
    top10_movies,
    x="일관객합계",
    y="영화명",
    orientation="h",
    custom_data=["일관객10위권일수"],
    title="영화별 기간 일관객 합계 TOP 10",
    labels={
        "일관객합계": "기간 일관객 합계",
        "영화명": "영화",
    },
)

fig_top10.update_traces(
    hovertemplate=(
        "영화: %{y}<br>"
        "기간 일관객 합계: %{x:,}명<br>"
        "10위권에 든 날수: %{customdata[0]}일"
        "<extra></extra>"
    )
)

fig_top10.update_layout(
    yaxis=dict(categoryorder="array", categoryarray=top10_movies["영화명"].tolist()),
    xaxis=dict(tickformat=",", separatethousands=True),
)

st.plotly_chart(fig_top10, use_container_width=True)
st.markdown("**이 그래프로 알 수 있는 것**")
st.empty()
st.divider()


# ============================================================
# 그래프 5
# ============================================================
st.header("그래프 5")
st.info("앞으로 추가할 그래프를 이 구역에 넣습니다.")
