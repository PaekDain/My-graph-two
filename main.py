import datetime
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# 1. 페이지 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간", page_icon="🎬", layout="wide"
)

# 앱 제목 및 설명
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.markdown(
    "일별 박스오피스 데이터를 바탕으로 시간의 흐름에 따른 영화 관객 수 및 각종 지표 변화를 탐색합니다."
)
st.markdown("---")


# 2. KOBIS API 데이터 수집 함수 (2025~2026년 최신 데이터 가져오기)
def fetch_kobis_recent_data(api_key=""):
    """KOBIS API를 통해 최근 박스오피스 데이터를 가져오는 함수"""
    if not api_key:
        # API 키가 없을 때 기본 제공할 2025-2026년 가상/샘플 데이터 생성
        sample_2025_2026 = [
            # 2025년 데이터 예시
            {
                "날짜": "2025-01-01",
                "순위": 1,
                "영화명": "검은 수녀들",
                "일관객": 350000,
                "누적관객": 350000,
                "스크린수": 1500,
                "상영횟수": 6000,
            },
            {
                "날짜": "2025-01-02",
                "순위": 1,
                "영화명": "검은 수녀들",
                "일관객": 280000,
                "누적관객": 630000,
                "스크린수": 1480,
                "상영횟수": 5900,
            },
            {
                "날짜": "2025-05-05",
                "순위": 1,
                "영화명": "캡틴 아메리카: 브레이브 뉴 월드",
                "일관객": 520000,
                "누적관객": 2100000,
                "스크린수": 1800,
                "상영횟수": 7500,
            },
            {
                "날짜": "2025-12-25",
                "순위": 1,
                "영화명": "아바타: 불과 재",
                "일관객": 850000,
                "누적관객": 3200000,
                "스크린수": 2200,
                "상영횟수": 9000,
            },
            # 2026년 데이터 예시
            {
                "날짜": "2026-01-01",
                "순위": 1,
                "영화명": "아바타: 불과 재",
                "일관객": 620000,
                "누적관객": 6800000,
                "스크린수": 2100,
                "상영횟수": 8500,
            },
            {
                "날짜": "2026-02-17",
                "순위": 1,
                "영화명": "2026 설날 흥행작",
                "일관객": 450000,
                "누적관객": 1200000,
                "스크린수": 1600,
                "상영횟수": 6800,
            },
            {
                "날짜": "2026-05-05",
                "순위": 1,
                "영화명": "어벤져스: 도둠스데이 Pre",
                "일관객": 780000,
                "누적관객": 2900000,
                "스크린수": 2000,
                "상영횟수": 8200,
            },
        ]
        return pd.DataFrame(sample_2025_2026)

    # API 키가 있을 때 KOBIS Open API 호출 (최근 7일 예시)
    records = []
    today = datetime.date.today()
    for i in range(1, 8):
        target_date = (today - datetime.timedelta(days=i)).strftime("%Y%m%d")
        url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={api_key}&targetDt={target_date}"
        try:
            res = requests.get(url, timeout=5).json()
            daily_list = res.get("boxOfficeResult", {}).get(
                "dailyBoxOfficeList", []
            )
            for item in daily_list:
                records.append(
                    {
                        "날짜": target_date,
                        "순위": int(item.get("rank", 0)),
                        "영화명": item.get("movieNm", ""),
                        "일관객": int(item.get("audiCnt", 0)),
                        "누적관객": int(item.get("audiAcc", 0)),
                        "스크린수": int(item.get("scrnCnt", 0)),
                        "상영횟수": int(item.get("showCnt", 0)),
                    }
                )
        except Exception:
            continue

    return pd.DataFrame(records)


# 3. 데이터 불러오기 및 전처리 (기존 CSV + 2025/2026 데이터 병합)
@st.cache_data
def load_data(kobis_api_key=""):
    # 1) 기존 GitHub CSV 로드
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"
    df_old = pd.read_csv(url)
    df_old["날짜"] = pd.to_datetime(
        df_old["날짜"].astype(str), format="%Y%m%d"
    )

    # 2) 2025~2026년 데이터 수집/생성
    df_recent = fetch_kobis_recent_data(kobis_api_key)
    if not df_recent.empty:
        df_recent["날짜"] = pd.to_datetime(df_recent["날짜"])

    # 3) 데이터 병합 (Concat) 및 중복 제거
    df = pd.concat([df_old, df_recent], ignore_index=True)
    df = df.drop_duplicates(subset=["날짜", "영화명"]).sort_values("날짜")

    # 수치형 데이터 형변환
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# 사이드바 API 키 입력 옵션
st.sidebar.header("🔑 API 설정 (선택)")
kobis_key = st.sidebar.text_input(
    "KOBIS API Key (미입력 시 샘플 2025-2026 데이터 적용)",
    type="password",
)

try:
    raw_df = load_data(kobis_key)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

# 전체 영화 목록 (가나다순 정렬)
all_movies_sorted = sorted(raw_df["영화명"].dropna().unique().tolist())

# -----------------------------------------------------------------------------
# 사이드바: 날짜 범위 선택 기능
# -----------------------------------------------------------------------------
st.sidebar.header("🗓️ 날짜 범위 선택")
min_date = raw_df["날짜"].min().date()
max_date = raw_df["날짜"].max().date()

selected_date_range = st.sidebar.date_input(
    "조회할 기간을 지정하세요:",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

# 선택한 날짜에 맞춰 데이터 필터링
if len(selected_date_range) == 2:
    start_date, end_date = selected_date_range
    df = raw_df[
        (raw_df["날짜"].dt.date >= start_date)
        & (raw_df["날짜"].dt.date <= end_date)
    ].copy()
else:
    df = raw_df.copy()

if df.empty:
    st.warning("선택한 기간에 해당하는 데이터가 없습니다.")
    st.stop()


# -----------------------------------------------------------------------------
# 구역 1: 영화별 일관객 변화
# -----------------------------------------------------------------------------
st.header("📌 구역 1: 영화별 일관객 변화")

selected_movie = st.selectbox(
    "조회할 영화를 선택하거나 검색하세요 (2025~2026 개봉작 포함):",
    options=all_movies_sorted,
    index=0,
    key="select_q1",
)

movie_df = df[df["영화명"] == selected_movie].sort_values("날짜")

if not movie_df.empty:
    fig1 = px.line(
        movie_df,
        x="날짜",
        y="일관객",
        title=f"[{selected_movie}] 날짜별 일관객 수 변화",
        labels={"날짜": "날짜", "일관객": "일일 관객 수(명)"},
        markers=True,
        hover_data={
            "날짜": "|%Y-%m-%d",
            "일관객": ":,d",
            "순위": True,
            "스크린수": ":,d",
        },
    )

    fig1.update_traces(
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<br><b>순위:</b> %{customdata[0]}위<br><b>스크린수:</b> %{customdata[1]:,}개<extra></extra>",
        line=dict(width=2.5, color="#E50914"),
        marker=dict(size=6),
    )

    fig1.update_layout(
        xaxis_title="날짜",
        yaxis_title="일일 관객 수 (명)",
        hovermode="x unified",
        margin=dict(l=20, r=20, t=50, b=20),
        height=450,
    )

    st.plotly_chart(fig1, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("최고 일관객 수", f"{movie_df['일관객'].max():,} 명")
    col2.metric("최대 스크린 수", f"{movie_df['스크린수'].max():,} 개")
    col3.metric("차트 진입 일수", f"{len(movie_df)} 일")
    col4.metric("기간 내 누적 관객 수", f"{movie_df['일관객'].sum():,} 명")
else:
    st.warning(
        f"선택한 기간 내에 [{selected_movie}]의 상영 데이터가 없습니다."
    )

if "note_1" not in st.session_state:
    st.session_state.note_1 = ""

user_input_1 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_1,
    key="input_1",
    placeholder="그래프를 보고 발견한 인사이트를 기록하세요...",
)
if st.button("💾 구역 1 메모 저장", key="btn_1"):
    st.session_state.note_1 = user_input_1
    st.success("구역 1 인사이트 메모가 저장되었습니다!")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 2: 주요 TOP 5 흥행작 동시 관객 수 비교
# -----------------------------------------------------------------------------
st.header("📌 구역 2: 주요 TOP 5 흥행작 동시 관객 수 비교")

top5_movies = (
    df.groupby("영화명")["일관객"].sum().nlargest(5).index.tolist()
)
top5_df = df[df["영화명"].isin(top5_movies)].sort_values("날짜")

if not top5_df.empty:
    fig2 = px.line(
        top5_df,
        x="날짜",
        y="일관객",
        color="영화명",
        title="기간 내 일관객 TOP 5 영화 날짜별 추이 비교",
        labels={
            "날짜": "날짜",
            "일관객": "일일 관객 수(명)",
            "영화명": "영화 제목",
        },
    )

    fig2.update_traces(
        mode="lines+markers",
        hovertemplate="<b>영화명:</b> %{fullData.name}<br><b>날짜:</b> %{x|%Y-%m-%d}<br><b>일관객:</b> %{y:,}명<extra></extra>",
    )

    fig2.update_layout(
        xaxis_title="날짜",
        yaxis_title="일일 관객 수 (명)",
        hovermode="x unified",
        legend=dict(
            title="영화 제목 (클릭하여 켜기/끄기)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin=dict(l=20, r=20, t=60, b=20),
        height=500,
    )

    st.plotly_chart(fig2, use_container_width=True)

if "note_2" not in st.session_state:
    st.session_state.note_2 = ""

user_input_2 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_2,
    key="input_2",
    placeholder="그래프를 보고 발견한 인사이트를 기록하세요...",
)
if st.button("💾 구역 2 메모 저장", key="btn_2"):
    st.session_state.note_2 = user_input_2
    st.success("구역 2 인사이트 메모가 저장되었습니다!")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 3: 날짜별 관객 수 추이 및 특정 영화 비교
# -----------------------------------------------------------------------------
st.header(
    "📌 구역 3: 날짜별 박스오피스 총 관객 수 추이 및 특정 영화 비교"
)

selected_movies_q3 = st.multiselect(
    "조회할 영화를 선택하세요 (비워두면 전체 영화 합계로 표시됩니다):",
    options=all_movies_sorted,
    default=[],
    key="select_q3",
)

if selected_movies_q3:
    filtered_q3_df = df[df["영화명"].isin(selected_movies_q3)]
    chart_title = (
        f"선택한 {len(selected_movies_q3)}개 영화의 일별 관객 수 총합"
    )
else:
    filtered_q3_df = df
    chart_title = "일별 박스오피스 전체 영화 관객 수 총합"

daily_total = (
    filtered_q3_df.groupby("날짜")["일관객"]
    .sum()
    .reset_index()
    .sort_values("날짜")
)

if not daily_total.empty:
    top3_days = daily_total.nlargest(3, "일관객").sort_values("날짜")

    fig3 = px.area(
        daily_total,
        x="날짜",
        y="일관객",
        title=chart_title,
        labels={"날짜": "날짜", "일관객": "총 관객 수(명)"},
    )

    fig3.update_traces(
        line_color="#2E86C1",
        fillcolor="rgba(46, 134, 193, 0.3)",
        hovertemplate="<b>날짜:</b> %{x|%Y-%m-%d}<br><b>관객수:</b> %{y:,}명<extra></extra>",
    )

    fig3.add_trace(
        go.Scatter(
            x=top3_days["날짜"],
            y=top3_days["일관객"],
            mode="markers+text",
            name="최대 관객 3일",
            text=[
                f"🏆 {d.strftime('%Y-%m-%d')}<br>({v:,.0f}명)"
                for d, v in zip(top3_days["날짜"], top3_days["일관객"])
            ],
            textposition="top center",
            marker=dict(size=12, color="#E74C3C", symbol="star"),
            hoverinfo="skip",
        )
    )

    fig3.update_layout(
        xaxis_title="날짜",
        yaxis_title="일관객 합계 (명)",
        hovermode="x unified",
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20),
        height=500,
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("🔥 관객 수가 가장 많았던 Top 3 날짜 및 메타 작성")
    cols = st.columns(3)

    for idx, (_, row) in enumerate(
        top3_days.sort_values("일관객", ascending=False).iterrows()
    ):
        date_str = row["날짜"].strftime("%Y-%m-%d")
        cols[idx].metric(
            label=f"{idx+1}위: {date_str}", value=f"{row['일관객']:,} 명"
        )

        note_key = f"date_note_{date_str}"
        if note_key not in st.session_state:
            st.session_state[note_key] = ""

        st.session_state[note_key] = cols[idx].text_input(
            f"📝 {date_str} 메모:",
            value=st.session_state[note_key],
            key=f"input_date_{date_str}",
            placeholder="예: 설 연휴, 신작 개봉일 등",
        )

if "note_3" not in st.session_state:
    st.session_state.note_3 = ""

user_input_3 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_3,
    key="input_3",
    placeholder="그래프를 보고 발견한 인사이트를 기록하세요...",
)
if st.button("💾 구역 3 메모 저장", key="btn_3"):
    st.session_state.note_3 = user_input_3
    st.success("구역 3 인사이트 메모가 저장되었습니다!")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 4: TOP 10 영화 비교
# -----------------------------------------------------------------------------
st.header("📌 구역 4: 기간 내 관객 수 TOP 10 영화")

metric_option = st.radio(
    "집계 기준을 선택하세요:",
    options=["기간 내 일관객 합계", "최종 누적관객 수"],
    horizontal=True,
)

top10_movies_summary = (
    df.groupby("영화명")
    .agg(
        일관객합계=("일관객", "sum"),
        누적관객수=("누적관객", "max"),
        진입일수=("날짜", "nunique"),
    )
    .reset_index()
)

if not top10_movies_summary.empty:
    if metric_option == "기간 내 일관객 합계":
        target_col = "일관객합계"
        chart_title = "기간 내 일관객 합계 TOP 10 영화"
    else:
        target_col = "누적관객수"
        chart_title = "최종 누적관객 수 TOP 10 영화"

    top10_movies_summary = top10_movies_summary.nlargest(
        10, target_col
    ).sort_values(target_col, ascending=True)

    fig4 = px.bar(
        top10_movies_summary,
        x=target_col,
        y="영화명",
        orientation="h",
        title=chart_title,
        labels={target_col: f"{metric_option}(명)", "영화명": "영화 제목"},
        text=target_col,
    )

    fig4.update_traces(
        texttemplate="%{text:,.0f}명",
        textposition="outside",
        marker_color=(
            "#3498DB" if metric_option == "기간 내 일관객 합계" else "#2ECC71"
        ),
        customdata=top10_movies_summary[
            ["진입일수", "일관객합계", "누적관객수"]
        ],
        hovertemplate=(
            "<b>영화명:</b> %{y}<br>"
            f"<b>{metric_option}:</b> %{{x:,}}명<br>"
            "<b>일관객 합계:</b> %{customdata[1]:,}명<br>"
            "<b>최종 누적관객:</b> %{customdata[2]:,}명<br>"
            "<b>차트 진입 일수:</b> %{customdata[0]}일<extra></extra>"
        ),
    )

    fig4.update_layout(
        xaxis_title=f"{metric_option} (명)",
        yaxis_title="영화명",
        margin=dict(l=20, r=80, t=50, b=20),
        height=500,
    )

    st.plotly_chart(fig4, use_container_width=True)

if "note_4" not in st.session_state:
    st.session_state.note_4 = ""

user_input_4 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_4,
    key="input_4",
    placeholder="그래프를 보고 발견한 인사이트를 기록하세요...",
)
if st.button("💾 구역 4 메모 저장", key="btn_4"):
    st.session_state.note_4 = user_input_4
    st.success("구역 4 인사이트 메모가 저장되었습니다!")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 5: 월×요일별 일관객 합계 (히트맵)
# -----------------------------------------------------------------------------
st.header("📌 구역 5: 월×요일별 관객 수 분포")

heatmap_df = df.copy()
heatmap_df["월"] = heatmap_df["날짜"].dt.month.astype(str) + "월"
heatmap_df["요일"] = heatmap_df["날짜"].dt.day_name()

day_map = {
    "Monday": "월요일",
    "Tuesday": "화요일",
    "Wednesday": "수요일",
    "Thursday": "목요일",
    "Friday": "금요일",
    "Saturday": "토요일",
    "Sunday": "일요일",
}
heatmap_df["요일"] = heatmap_df["요일"].map(day_map)

days_order = [
    "월요일",
    "화요일",
    "수요일",
    "목요일",
    "금요일",
    "토요일",
    "일요일",
]
months_order = [f"{i}월" for i in range(1, 13)]

pivot_df = (
    heatmap_df.pivot_table(
        index="월", columns="요일", values="일관객", aggfunc="sum"
    )
    .reindex(index=months_order, columns=days_order)
    .fillna(0)
)

fig5 = px.imshow(
    pivot_df,
    labels=dict(x="요일", y="월", color="일관객 합계"),
    x=days_order,
    y=months_order,
    color_continuous_scale="Reds",
    aspect="auto",
    title="월 및 요일별 일관객 합계 히트맵",
)

fig5.update_traces(
    hovertemplate="<b>%{y} %{x}</b><br>일관객 합계: %{z:,}명<extra></extra>"
)

fig5.update_layout(
    xaxis_title="요일",
    yaxis_title="월",
    margin=dict(l=20, r=20, t=50, b=20),
    height=500,
)

st.plotly_chart(fig5, use_container_width=True)

if "note_5" not in st.session_state:
    st.session_state.note_5 = ""

user_input_5 = st.text_area(
    "💡 이 그래프로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_5,
    key="input_5",
    placeholder="그래프를 보고 발견한 인사이트를 기록하세요...",
)
if st.button("💾 구역 5 메모 저장", key="btn_5"):
    st.session_state.note_5 = user_input_5
    st.success("구역 5 인사이트 메모가 저장되었습니다!")

st.markdown("---")

# -----------------------------------------------------------------------------
# 구역 6: 개봉 영화 종합 정보 조회 (영화명 - 관객수 - 첫 상영일 - 마지막 상영일)
# -----------------------------------------------------------------------------
st.header("📌 구역 6: 개봉 영화 종합 정보 조회")

selected_movie_q6 = st.selectbox(
    "조회할 영화를 선택하세요 (2025~2026년 영화 포함):",
    options=all_movies_sorted,
    index=0,
    key="select_q6",
)

q6_movie_df = raw_df[raw_df["영화명"] == selected_movie_q6].sort_values("날짜")

if not q6_movie_df.empty:
    first_date = q6_movie_df["날짜"].min().strftime("%Y-%m-%d")
    last_date = q6_movie_df["날짜"].max().strftime("%Y-%m-%d")
    total_period_audience = q6_movie_df["일관객"].sum()
    max_accum_audience = q6_movie_df["누적관객"].max()

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("🎬 영화 이름", selected_movie_q6)
    m_col2.metric(
        "👥 총 관객 수 (기간 합계 / 최고 누적)",
        f"{total_period_audience:,} 명",
        f"최종 {max_accum_audience:,.0f} 명",
    )
    m_col3.metric("📅 첫 상영 날짜", first_date)
    m_col4.metric("🏁 마지막 상영 날짜", last_date)

    st.subheader(f"📊 [{selected_movie_q6}] 상영 정보 상세")
    st.dataframe(
        q6_movie_df[
            ["날짜", "순위", "일관객", "누적관객", "스크린수", "상영횟수"]
        ].assign(날짜=q6_movie_df["날짜"].dt.strftime("%Y-%m-%d")),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("선택한 영화의 데이터가 존재하지 않습니다.")

if "note_6" not in st.session_state:
    st.session_state.note_6 = ""

user_input_6 = st.text_area(
    "💡 이 구역으로 알 수 있는 것 (직접 입력):",
    value=st.session_state.note_6,
    key="input_6",
    placeholder="영화 상세 정보 분석 인사이트를 기록하세요...",
)
if st.button("💾 구역 6 메모 저장", key="btn_6"):
    st.session_state.note_6 = user_input_6
    st.success("구역 6 인사이트 메모가 저장되었습니다!")
