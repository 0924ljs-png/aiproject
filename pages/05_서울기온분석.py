
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(
    page_title="월별 기온분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 월별 기온분석")
st.write("원하는 월을 선택하여 연도별 최고기온과 최저기온을 비교해 보세요!")

# CSV 파일 찾기
folder = Path(__file__).resolve().parent

possible_paths = [
    folder / "기온데이터_UTF8.csv",
    folder / "extremum_20261109105046.csv",
    folder.parent / "기온데이터_UTF8.csv",
    folder.parent / "extremum_20261109105046.csv",
]

csv_path = next(
    (p for p in possible_paths if p.exists()),
    None
)

if csv_path is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info("기온데이터_UTF8.csv 파일을 app.py와 같은 폴더에 넣어 주세요.")
    st.stop()

# 데이터 불러오기
@st.cache_data
def load_data(path):
    try:
        data = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(path, encoding="cp949")

    required = ["일시", "최고기온(℃)", "최저기온(℃)"]

    for col in required:
        if col not in data.columns:
            raise ValueError(f"필요한 열이 없습니다: {col}")

    # 두 자리 연도를 실제 연도로 복원
    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }

    century = 1900
    previous_year = None
    dates = []

    for value in data["일시"].astype(str).str.strip():
        try:
            month_text, year_text = value.split("-")
            month = month_dict[month_text]
            year = int(year_text)

            if (
                previous_year is not None
                and year < previous_year
                and previous_year >= 90
                and year <= 10
            ):
                century += 100

            full_year = century + year

            dates.append(
                pd.Timestamp(full_year, month, 1)
            )

            previous_year = year

        except (ValueError, KeyError):
            dates.append(pd.NaT)

    data["날짜"] = dates

    data["최고기온(℃)"] = pd.to_numeric(
        data["최고기온(℃)"], errors="coerce"
    )

    data["최저기온(℃)"] = pd.to_numeric(
        data["최저기온(℃)"], errors="coerce"
    )

    data = data.dropna(
        subset=["날짜", "최고기온(℃)", "최저기온(℃)"]
    ).copy()

    data["연도"] = data["날짜"].dt.year
    data["월"] = data["날짜"].dt.month

    return data


try:
    df = load_data(str(csv_path))
except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()

if df.empty:
    st.warning("분석할 데이터가 없습니다.")
    st.stop()

# 월 선택
month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

available_months = sorted(df["월"].unique())

selected_month = st.selectbox(
    "📅 분석할 월을 선택하세요.",
    available_months,
    format_func=lambda x: month_names[int(x)]
)

# 선택한 월의 데이터
monthly_df = df[df["월"] == selected_month]

# 연도별 최고기온과 최저기온
yearly_df = (
    monthly_df.groupby("연도", as_index=False)
    .agg({
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .sort_values("연도")
)

# 그래프 생성
fig = go.Figure()

# 최고기온 - 핫핑크
fig.add_trace(
    go.Scatter(
        x=yearly_df["연도"],
        y=yearly_df["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(color="hotpink", width=3),
        marker=dict(size=8)
    )
)

# 최저기온 - 하늘색
fig.add_trace(
    go.Scatter(
        x=yearly_df["연도"],
        y=yearly_df["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(color="skyblue", width=3),
        marker=dict(size=8)
    )
)

# 그래프 제목과 축 설정
fig.update_layout(
    title="월별 기온분석",
    xaxis_title="연도",
    yaxis_title="온도(℃)",
    legend_title="범례",
    hovermode="x unified",
    template="plotly_white",
    height=550
)

fig.update_xaxes(dtick=5)

# 그래프 출력
st.plotly_chart(
    fig,
    use_container_width=True
)

# 데이터 표
st.subheader(
    f"📊 {month_names[int(selected_month)]} 연도별 기온 데이터"
)

st.dataframe(
    yearly_df,
    use_container_width=True,
    hide_index=True
)

# 요약 정보
col1, col2 = st.columns(2)

with col1:
    hottest = yearly_df.loc[
        yearly_df["최고기온(℃)"].idxmax()
    ]

    st.metric(
        "가장 높았던 최고기온",
        f'{hottest["최고기온(℃)"]:.1f}℃',
        f'{int(hottest["연도"])}년'
    )

with col2:
    coldest = yearly_df.loc[
        yearly_df["최저기온(℃)"].idxmin()
    ]

    st.metric(
        "가장 낮았던 최저기온",
        f'{coldest["최저기온(℃)"]:.1f}℃',
        f'{int(coldest["연도"])}년'
    )

st.caption(f"사용 데이터: {csv_path.name}")
