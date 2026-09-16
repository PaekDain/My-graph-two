import streamlit as st
import pandas as pd
import plotly.express as px

# 1. 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide"
)

# 앱 제목 및 설명
st.title("🎬 영화 데이터 그래프 도감 2 - 분포와 관계")
st.markdown("박스오피스 주요 개봉 영화 216편의 데이터를 바탕으로 장르, 국가, 스크린 수, 관객 수 간의 분포와 관계를 탐색합니다.")
st.markdown("---")


# 2. 데이터 불러오기 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # openDt 열을 datetime 형식으로 변환 (YYYYMMDD -> YYYY-MM-DD)
    if 'openDt' in df.columns:
        df['openDt'] = pd.to_datetime(df['openDt'].astype(str), format='%Y%m%d', errors='coerce')

    # genre 열 전처리: '|' 기호로 연결된 여러 장르 중 첫 번째 장르만 선택
    if 'genre' in df.columns:
        df['genre_first'] = df['genre'].fillna('기타').astype(str).apply(lambda x: x.split('|')[0].strip())

    # 수치형 데이터 형변환
    numeric_cols = ['first_scrn', 'first_show', 'first_week_audi', 'total_audi', 'days_in_top10']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

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

# 장르별 영화 수 집계
genre_counts = df['genre_first'].value_counts().reset_index()
genre_counts.columns = ['장르', '영화편수']

# Plotly 도넛 그래프 생성
fig1 = px.pie(
    genre_counts,
    names='장르',
    values='영화편수',
    title="대표 장르별 영화 편수 비중",
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Pastel
)

fig1.update_traces(
    textinfo='label+percent',
    hovertemplate="<b>장르:</b> %{label}<br><b>영화 편수:</b> %{value}편<br><b>비율:</b> %{percent}<extra></extra>"
)

fig1.update_layout(
    margin=dict(l=20, r=20, t=50, b=20),
    height=500,
    legend_title="장르"
)

st.plotly_chart(fig1, use_container_width=True)

if 'note_1' not in st.session_state:
    st.session_state.note_1 = ""

user_input_1 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_1,
    key="input_1",
    placeholder="예: 특정 장르가 전체 개봉작 중 가장 큰 비중을 차지하는 것을 확인할 수 있습니다..."
)
if st.button("💾 구역 1 메모 저장", key="btn_1"):
    st.session_state.note_1 = user_input_1
    st.success("구역 1 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 2: 장르 및 영화별 총 관객 수 분포 (트리맵)
# -----------------------------------------------------------------------------
st.header("📌 구역 2: 장르별 영화 총 관객 수 분포")

treemap_df = df.dropna(subset=['total_audi', 'genre_first', 'movieNm']).copy()

fig2 = px.treemap(
    treemap_df,
    path=[px.Constant("전체 장르"), 'genre_first', 'movieNm'],
    values='total_audi',
    color='genre_first',
    title="장르 및 영화별 총 관객 수 (칸 크기 = 총 관객 수)",
    color_discrete_sequence=px.colors.qualitative.Set3
)

fig2.update_traces(
    hovertemplate="<b>영화명/구분:</b> %{label}<br><b>총 관객 수:</b> %{value:,}명<extra></extra>"
)

fig2.update_layout(
    margin=dict(l=20, r=20, t=50, b=20),
    height=600
)

st.plotly_chart(fig2, use_container_width=True)

if 'note_2' not in st.session_state:
    st.session_state.note_2 = ""

user_input_2 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_2,
    key="input_2",
    placeholder="예: 특정 장르 내에서 흥행을 주도한 대표 영화와 관객 수 비중을 한눈에 비교할 수 있습니다..."
)
if st.button("💾 구역 2 메모 저장", key="btn_2"):
    st.session_state.note_2 = user_input_2
    st.success("구역 2 인사이트 메모가 저장되었습니다!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 구역 3: 총 관객 수 분포 (히스토그램)
# -----------------------------------------------------------------------------
st.header("📌 구역 3: 총 관객 수 히스토그램")

hist_df = df.dropna(subset=['total_audi']).copy()

# 가장 관객 수가 많은 영화 계산
top_movie_row = hist_df.loc[hist_df['total_audi'].idxmax()]
top_movie_name = top_movie_row['movieNm']
top_movie_audi = int(top_movie_row['total_audi'])

# Plotly 히스토그램 생성
fig3 = px.histogram(
    hist_df,
    x='total_audi',
    nbins=30,
    title="영화별 총 관객 수 분포",
    labels={'total_audi': '총 관객 수 (명)'},
    color_discrete_sequence=['#2E86C1']
)

fig3.update_traces(
    hovertemplate="<b>총 관객 수 구간:</b> %{x}명<br><b>영화 수:</b> %{y}편<extra></extra>"
)

fig3.update_layout(
    xaxis_title="총 관객 수 (명)",
    yaxis_title="영화 수 (편)",
    margin=dict(l=20, r=20, t=50, b=20),
    height=450
)

st.plotly_chart(fig3, use_container_width=True)

# 그래프 하단 정보 문구
st.write(f"📊 **대부분의 영화가 몰려 있는 구간:** 약 100만 명 미만 구간에 대부분의 개봉작이 집중되어 있습니다.")
st.write(f"🏆 **가장 관객이 많은 영화:** **{top_movie_name}** ({top_movie_audi:,}명)")

if 'note_3' not in st.session_state:
    st.session_state.note_3 = ""

user_input_3 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_3,
    key="input_3",
    placeholder="예: 대다수 영화가 소형 관객 구간에 밀집되어 있으며, 대형 흥행작은 소수에 불과한 롱테일 분포를 파악할 수 있습니다..."
)
if st.button("💾 구역 3 메모 저장", key="btn_3"):
    st.session_state.note_3 = user_input_3
    st.success("구역 3 인사이트 메모가 저장되었습니다!")
