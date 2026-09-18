import pandas as pd
import plotly.express as px
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

# 앱 제목 및 설명
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown(
    "박스오피스 주요 개봉 영화 216편의 데이터를 바탕으로 장르, 국가, 스크린 수, 관객 수 간의 분포와 관계를 탐색합니다."
)
st.markdown("---")


# 2. 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # openDt 열을 datetime 형식으로 변환 (YYYYMMDD -> YYYY-MM-DD)
    if "openDt" in df.columns:
        df["openDt"] = pd.to_datetime(
            df["openDt"].astype(str), format="%Y%m%d", errors="coerce"
        )

    # genre 열 전처리: '|' 기호로 연결된 여러 장르 중 첫 번째 장르만 선택
    if "genre" in df.columns:
        df["genre_first"] = (
            df["genre"]
            .fillna("기타")
            .astype(str)
            .apply(lambda x: x.split("|")[0].strip())
        )

    # nation 열 결측치 처리
    if "nation" in df.columns:
        df["nation"] = df["nation"].fillna("기타")

    # 수치형 데이터 형변환
    numeric_cols = [
        "first_scrn",
        "first_show",
        "first_week_audi",
        "total_audi",
        "days_in_top10",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# -----------------------------------------------------------------------------
# 구역 1: 장르별 영화 편수 분포 (도넛 그래프)
# -----------------------------------------------------------------------------
st.header("📌 구역 1: 장르별 영화 편수 분포")

genre_counts = df["genre_first"].value_counts().reset_index()
genre_counts.columns = ["장르", "영화편수"]

fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화편수",
    title="대표 장르별 영화 편수 비중",
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Pastel,
)

fig1.update_traces(
    textinfo="label+percent",
    hovertemplate="<b>장르:</b> %{label}<br><b>영화 편수:</b> %{value}편<br><b>비율:</b> %{percent}<extra></extra>",
)

fig1.update_layout(
    margin=dict(l=20, r=20, t=50, b=20), height=500, legend_title="장르"
)

st.plotly_chart(fig1, use_container_width=True)

if "note_1" not in st.session_state:
    st.session_state.note_1 = ""

user_input_1 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_1,
    key="input_1",
    placeholder="예: 특정 장르가 전체 개봉작 중 가장 큰 비중을 차지하는 것을 확인할 수 있습니다...",
)
if st.button("💾 구역 1 메모 저장", key="btn_1"):
    st.session_state.note_1 = user_input_1
    st.success("구역 1 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 2: 장르 및 영화별 총 관객 수 분포 (트리맵)
# -----------------------------------------------------------------------------
st.header("📌 구역 2: 장르별 영화 총 관객 수 분포")

treemap_df = df.dropna(subset=["total_audi", "genre_first", "movieNm"]).copy()

fig2 = px.treemap(
    treemap_df,
    path=[px.Constant("전체 장르"), "genre_first", "movieNm"],
    values="total_audi",
    color="genre_first",
    title="장르 및 영화별 총 관객 수 (칸 크기 = 총 관객 수)",
    color_discrete_sequence=px.colors.qualitative.Set3,
)

fig2.update_traces(
    hovertemplate="<b>영화명/구분:</b> %{label}<br><b>총 관객 수:</b> %{value:,}명<extra></extra>"
)

fig2.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=600)

st.plotly_chart(fig2, use_container_width=True)

if "note_2" not in st.session_state:
    st.session_state.note_2 = ""

user_input_2 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_2,
    key="input_2",
    placeholder="예: 특정 장르 내에서 흥행을 주도한 대표 영화와 관객 수 비중을 한눈에 비교할 수 있습니다...",
)
if st.button("💾 구역 2 메모 저장", key="btn_2"):
    st.session_state.note_2 = user_input_2
    st.success("구역 2 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 3: 총 관객 수 분포 (히스토그램)
# -----------------------------------------------------------------------------
st.header("📌 구역 3: 총 관객 수 히스토그램")

hist_df = df.dropna(subset=["total_audi"]).copy()

top_movie_row = hist_df.loc[hist_df["total_audi"].idxmax()]
top_movie_name = top_movie_row["movieNm"]
top_movie_audi = int(top_movie_row["total_audi"])

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=30,
    title="영화별 총 관객 수 분포",
    labels={"total_audi": "총 관객 수 (명)"},
    color_discrete_sequence=["#2E86C1"],
)

fig3.update_traces(
    hovertemplate="<b>총 관객 수 구간:</b> %{x}명<br><b>영화 수:</b> %{y}편<extra></extra>"
)

fig3.update_layout(
    xaxis_title="총 관객 수 (명)",
    yaxis_title="영화 수 (편)",
    margin=dict(l=20, r=20, t=50, b=20),
    height=450,
)

st.plotly_chart(fig3, use_container_width=True)

st.write(
    f"📊 **대부분의 영화가 몰려 있는 구간:** 약 100만 명 미만 구간에 대부분의 개봉작이 집중되어 있습니다."
)
st.write(
    f"🏆 **가장 관객이 많은 영화:** **{top_movie_name}** ({top_movie_audi:,}명)"
)

if "note_3" not in st.session_state:
    st.session_state.note_3 = ""

user_input_3 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_3,
    key="input_3",
    placeholder="예: 대다수 영화가 소형 관객 구간에 밀집되어 있으며, 대형 흥행작은 소수에 불과한 롱테일 분포를 파악할 수 있습니다...",
)
if st.button("💾 구역 3 메모 저장", key="btn_3"):
    st.session_state.note_3 = user_input_3
    st.success("구역 3 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 4: 개봉일 스크린 수 vs 총 관객 수 (산점도)
# -----------------------------------------------------------------------------
st.header("📌 구역 4: 개봉일 스크린 수 vs 총 관객 수 산점도")

scatter_df = df.dropna(
    subset=["first_scrn", "total_audi", "genre_first", "movieNm"]
).copy()

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린 수와 총 관객 수의 관계",
    labels={
        "first_scrn": "개봉일 스크린 수 (개)",
        "total_audi": "총 관객 수 (명)",
        "genre_first": "장르",
    },
    color_discrete_sequence=px.colors.qualitative.Vivid,
)

fig4.update_traces(
    marker=dict(size=9, opacity=0.8),
    hovertemplate="<b>영화명: %{hovertext}</b><br>장르: %{fullData.name}<br>개봉일 스크린 수: %{x:,}개<br>총 관객 수: %{y:,}명<extra></extra>",
)

fig4.update_layout(
    xaxis_title="개봉일 스크린 수 (개)",
    yaxis_title="총 관객 수 (명)",
    margin=dict(l=20, r=20, t=50, b=20),
    height=550,
)

st.plotly_chart(fig4, use_container_width=True)

if "note_4" not in st.session_state:
    st.session_state.note_4 = ""

user_input_4 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_4,
    key="input_4",
    placeholder="예: 개봉일 스크린 수가 많을수록 총 관객 수도 증가하는 양의 상관관계가 있는지 분석할 수 있습니다...",
)
if st.button("💾 구역 4 메모 저장", key="btn_4"):
    st.session_state.note_4 = user_input_4
    st.success("구역 4 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 5: 개봉일 스크린 수 vs 총 관객 수 (버블 차트)
# -----------------------------------------------------------------------------
st.header("📌 구역 5: 개봉일 스크린 수 vs 총 관객 수 (버블 차트)")

bubble_df = df.dropna(
    subset=[
        "first_scrn",
        "total_audi",
        "genre_first",
        "movieNm",
        "first_week_audi",
    ]
).copy()

fig5_bubble = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일 스크린 수 vs 총 관객 수 (버블 크기 = 개봉 첫 주 관객 수)",
    labels={
        "first_scrn": "개봉일 스크린 수 (개)",
        "total_audi": "총 관객 수 (명)",
        "genre_first": "장르",
        "first_week_audi": "개봉 첫 주 관객 수",
    },
    color_discrete_sequence=px.colors.qualitative.Vivid,
    size_max=40,
)

fig5_bubble.update_traces(
    hovertemplate=(
        "<b>영화명: %{hovertext}</b><br>"
        "장르: %{fullData.name}<br>"
        "개봉일 스크린 수: %{x:,}개<br>"
        "총 관객 수: %{y:,}명<br>"
        "🎟️ 개봉 첫 주 관객 수: %{marker.size:,}명<extra></extra>"
    )
)

fig5_bubble.update_layout(
    xaxis_title="개봉일 스크린 수 (개)",
    yaxis_title="총 관객 수 (명)",
    margin=dict(l=20, r=20, t=50, b=20),
    height=550,
)

st.plotly_chart(fig5_bubble, use_container_width=True)

if "note_5" not in st.session_state:
    st.session_state.note_5 = ""

user_input_5 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_5,
    key="input_5",
    placeholder="예: 스크린 수와 총 관객 수뿐만 아니라, 초반 흥행 동력(첫 주 관객 수)이 전체 관객 수 및 스크린 확보에 미친 영향을 함께 비교할 수 있습니다...",
)
if st.button("💾 구역 5 메모 저장", key="btn_5"):
    st.session_state.note_5 = user_input_5
    st.success("구역 5 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 6: 주요 장르별 총 관객 수 박스플롯 (상자 그림)
# -----------------------------------------------------------------------------
st.header("📌 구역 6: 주요 장르별 총 관객 수 박스플롯")

genre_counts_series = df["genre_first"].value_counts()
top_genres = genre_counts_series[genre_counts_series >= 10].index.tolist()

box_df = (
    df[df["genre_first"].isin(top_genres)]
    .dropna(subset=["total_audi", "movieNm"])
    .copy()
)

fig6 = px.box(
    box_df,
    x="genre_first",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    points="outliers",
    title="영화 10편 이상 장르의 총 관객 수 분포 (아웃라이어 포함)",
    labels={"genre_first": "장르", "total_audi": "총 관객 수 (명)"},
    color_discrete_sequence=px.colors.qualitative.Set2,
)

fig6.update_traces(
    hovertemplate="<b>영화명: %{hovertext}</b><br>장르: %{x}<br>총 관객 수: %{y:,}명<extra></extra>"
)

fig6.update_layout(
    xaxis_title="장르 (영화 10편 이상)",
    yaxis_title="총 관객 수 (명)",
    showlegend=False,
    margin=dict(l=20, r=20, t=50, b=20),
    height=550,
)

st.plotly_chart(fig6, use_container_width=True)

if "note_6" not in st.session_state:
    st.session_state.note_6 = ""

user_input_6 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_6,
    key="input_6",
    placeholder="예: 장르별 평균 관객 분포와 함께 상자 밖으로 튀어나온 메가 히트 아웃라이어 영화의 특성을 비교 분석할 수 있습니다...",
)
if st.button("💾 구역 6 메모 저장", key="btn_6"):
    st.session_state.note_6 = user_input_6
    st.success("구역 6 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 7: 개봉일 및 영화별 종합 성과 버블 산점도
# -----------------------------------------------------------------------------
st.header("📌 구역 7: 개봉일 기준 영화별 종합 흥행 성과 분석")

cols_needed = [
    "openDt",
    "genre_first",
    "nation",
    "first_scrn",
    "first_show",
    "first_week_audi",
    "total_audi",
    "days_in_top10",
    "movieNm",
]
df_q7 = df.dropna(subset=cols_needed).copy()

fig7 = px.scatter(
    df_q7,
    x="openDt",
    y="total_audi",
    size="first_week_audi",
    color="genre_first",
    hover_name="movieNm",
    title="개봉일(X축) vs 총 관객 수(Y축) 버블 차트 (버블 크기 = 개봉 첫 주 관객 수)",
    labels={
        "openDt": "개봉일 (openDt)",
        "total_audi": "총 관객 수 (total_audi, 명)",
        "genre_first": "장르 (genre)",
        "first_week_audi": "개봉 첫 주 관객 수",
    },
    color_discrete_sequence=px.colors.qualitative.Dark24,
)

fig7.update_traces(
    hovertemplate=(
        "<b>영화명: %{hovertext}</b><br>"
        "📅 개봉일(openDt): %{x|%Y-%m-%d}<br>"
        "🎬 장르(genre): %{fullData.name}<br>"
        "🌍 제작국가(nation): %{customdata[0]}<br>"
        "📺 개봉일 스크린수(first_scrn): %{customdata[1]:,}개<br>"
        "🎥 개봉일 상영횟수(first_show): %{customdata[2]:,}회<br>"
        "🎟️ 개봉 첫 주 관객(first_week_audi): %{customdata[3]:,}명<br>"
        "🍿 총 관객(total_audi): %{y:,}명<br>"
        "🏆 10위권 머문 날수(days_in_top10): %{customdata[4]}일<extra></extra>"
    ),
    customdata=df_q7[
        [
            "nation",
            "first_scrn",
            "first_show",
            "first_week_audi",
            "days_in_top10",
        ]
    ],
)

fig7.update_layout(
    xaxis_title="개봉일 (openDt)",
    yaxis_title="총 관객 수 (total_audi, 명)",
    margin=dict(l=20, r=20, t=50, b=20),
    height=600,
)

st.plotly_chart(fig7, use_container_width=True)

if "note_7" not in st.session_state:
    st.session_state.note_7 = ""

user_input_7 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_7,
    key="input_7",
    placeholder="예: 개봉 시기별 흥행 규모와 개봉 첫 주 관객 수, 10위권 유지 기간 간의 종합적인 상관관계를 한눈에 시각화할 수 있습니다...",
)
if st.button("💾 구역 7 메모 저장", key="btn_7"):
    st.session_state.note_7 = user_input_7
    st.success("구역 7 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 8: 제작 국가 및 장르별 영화 편수 (선버스트 차트)
# -----------------------------------------------------------------------------
st.header("📌 구역 8: 제작 국가 및 장르별 영화 편수 구성")

# 국가별, 장르별 영화 편수 집계
sunburst_df = (
    df.groupby(["nation", "genre_first"]).size().reset_index(name="movie_count")
)

# Plotly 선버스트 차트 생성
fig8 = px.sunburst(
    sunburst_df,
    path=["nation", "genre_first"],
    values="movie_count",
    title="제작 국가 → 장르별 영화 편수 구성",
    color="nation",
    color_discrete_sequence=px.colors.qualitative.Pastel,
)

fig8.update_traces(
    hovertemplate="<b>구분:</b> %{label}<br><b>영화 편수:</b> %{value}편<extra></extra>"
)

fig8.update_layout(margin=dict(l=20, r=20, t=50, b=20), height=600)

st.plotly_chart(fig8, use_container_width=True)

if "note_8" not in st.session_state:
    st.session_state.note_8 = ""

user_input_8 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_8,
    key="input_8",
    placeholder="예: 각 제작 국가별로 어떤 장르의 영화가 주로 수입되거나 제작되었는지 편수 비중을 다층 구조로 계층적으로 파악할 수 있습니다...",
)
if st.button("💾 구역 8 메모 저장", key="btn_8"):
    st.session_state.note_8 = user_input_8
    st.success("구역 8 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 9: 사용자 자율 질문 분석 (10위권 유지 기간 vs 총 관객 수)
# -----------------------------------------------------------------------------
st.header("📌 구역 9: 10위권에 오래 머문 영화는 총 관객도 많은가")

df_q9 = df.dropna(
    subset=["days_in_top10", "total_audi", "movieNm", "genre_first"]
).copy()

fig9 = px.scatter(
    df_q9,
    x="days_in_top10",
    y="total_audi",
    color="genre_first",
    hover_name="movieNm",
    title="10위권에 오래 머문 영화는 총 관객도 많은가",
    labels={
        "days_in_top10": "10위권에 머문 날수 (days_in_top10)",
        "total_audi": "총 관객 수 (total_audi, 명)",
        "genre_first": "장르",
    },
    color_discrete_sequence=px.colors.qualitative.Bold,
)

fig9.update_traces(
    marker=dict(size=9, opacity=0.8),
    hovertemplate=(
        "<b>영화명: %{hovertext}</b><br>"
        "🏆 10위권 머문 날수: %{x}일<br>"
        "🍿 총 관객 수: %{y:,}명<br>"
        "🎬 장르: %{fullData.name}<extra></extra>"
    ),
)

fig9.update_layout(
    xaxis_title="10위권에 머문 날수 (일)",
    yaxis_title="총 관객 수 (명)",
    margin=dict(l=20, r=20, t=50, b=20),
    height=550,
)

st.plotly_chart(fig9, use_container_width=True)

if "note_9" not in st.session_state:
    st.session_state.note_9 = ""

user_input_9 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_9,
    key="input_9",
    placeholder="예: 10위권에 머문 일수가 길수록 총 관객 수도 비례하여 증가하는 뚜렷한 양의 상관관계를 확인할 수 있습니다...",
)
if st.button("💾 구역 9 메모 저장", key="btn_9"):
    st.session_state.note_9 = user_input_9
    st.success("구역 9 인사이트 메모가 저장되었습니다!")
