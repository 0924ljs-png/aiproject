
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="서울 기온 분석",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 기온 데이터 분석")
st.write("서울의 기온 데이터를 다양한 그래프로 분석해 보세요!")

# ==========================================
# 2. CSV 파일 찾기
# ==========================================

folder = Path(__file__).resolve().parent

possible_paths = [
    folder / "기온데이터_UTF8.csv",
    folder / "extremum_20261109105046.csv",
    folder.parent / "기온데이터_UTF8.csv",
    folder.parent / "extremum_20261109105046.csv",
    folder / "data" / "기온데이터_UTF8.csv",
    folder.parent / "data" / "기온데이터_UTF8.csv",
]

csv_path = next(
    (p for p in possible_paths if p.exists()),
    None
)

if csv_path is None:
    st.error("CSV 파일을 찾을 수 없습니다.")
    st.info(
        "기온데이터_UTF8.csv 파일을 app.py와 같은 폴더에 넣어 주세요."
    )
    st.stop()

# ==========================================
# 3. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(path):

    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="cp949")

    required = [
        "일시",
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in required:
        if col not in df.columns:
            raise ValueError(f"필요한 열이 없습니다: {col}")

    # 두 자리 연도를 실제 연도로 변환
    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    century = 1900
    previous_year = None
    dates = []

    for value in df["일시"].astype(str).str.strip():

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

    df["날짜"] = dates

    # 숫자 데이터 변환
    temperature_columns = [
        "평균기온(℃)",
        "최고기온(℃)",
        "최저기온(℃)"
    ]

    for col in temperature_columns:
        df[col] = pd.to_numeric(
            df[col], errors="coerce"
        )

    df = df.dropna(subset=["날짜"]).copy()

    df["연도"] = df["날짜"].dt.year
    df["월"] = df["날짜"].dt.month

    return df


try:
    df = load_data(str(csv_path))

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

if df.empty:
    st.warning("분석할 데이터가 없습니다.")
    st.stop()

# ==========================================
# 4. 공통 설정
# ==========================================

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

all_months = list(range(1, 13))
years = sorted(df["연도"].dropna().unique().tolist())

# 그래프 공통 디자인
def make_layout(fig, title):

    fig.update_layout(
        title=title,
        xaxis_title="월",
        yaxis_title="온도(℃)",
        legend_title="범례",
        hovermode="x unified",
        template="plotly_white",
        height=500,
        xaxis=dict(
            tickmode="array",
            tickvals=all_months,
            ticktext=[
                month_names[m] for m in all_months
            ]
        )
    )

    return fig


# ==========================================
# 기능 1. 전체 연도의 월별 평균기온
# ==========================================

st.header("📈 1. 서울의 월별 평균기온")

st.write(
    "전체 데이터의 연도별 기온을 월별로 평균하여 "
    "서울의 월별 평균기온을 확인합니다."
)

average_df = (
    df.groupby("월")["평균기온(℃)"]
    .mean()
    .reindex(all_months)
    .reset_index()
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=average_df["월"],
        y=average_df["평균기온(℃)"],
        mode="lines+markers",
        name="월별 평균기온",
        line=dict(
            color="orange",
            width=4
        ),
        marker=dict(size=10)
    )
)

make_layout(fig1, "서울의 월별 평균기온")

st.plotly_chart(
    fig1,
    use_container_width=True
)

# 월별 평균기온 표
with st.expander("월별 평균기온 데이터 보기"):

    show_avg = average_df.copy()

    show_avg["월"] = show_avg["월"].map(month_names)

    st.dataframe(
        show_avg,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ==========================================
# 기능 2. 연도 1개 선택
# ==========================================

st.header("📊 2. 선택한 연도의 최고기온과 최저기온")

st.write(
    "원하는 연도 하나를 선택하면 해당 연도의 "
    "월별 최고기온과 최저기온을 비교합니다."
)

selected_year = st.selectbox(
    "분석할 연도를 선택하세요.",
    years,
    index=len(years) - 1,
    key="single_year"
)

one_year_df = df[
    df["연도"] == selected_year
]

one_year_result = (
    one_year_df.groupby("월")
    .agg({
        "최고기온(℃)": "max",
        "최저기온(℃)": "min"
    })
    .reindex(all_months)
    .reset_index()
)

fig2 = go.Figure()

# 최고기온 핫핑크
fig2.add_trace(
    go.Scatter(
        x=one_year_result["월"],
        y=one_year_result["최고기온(℃)"],
        mode="lines+markers",
        name="최고기온",
        line=dict(
            color="hotpink",
            width=3
        ),
        marker=dict(size=9)
    )
)

# 최저기온 하늘색
fig2.add_trace(
    go.Scatter(
        x=one_year_result["월"],
        y=one_year_result["최저기온(℃)"],
        mode="lines+markers",
        name="최저기온",
        line=dict(
            color="skyblue",
            width=3
        ),
        marker=dict(size=9)
    )
)

make_layout(
    fig2,
    f"{selected_year}년 월별 최고기온과 최저기온"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

with st.expander("선택한 연도의 기온 데이터 보기"):

    st.dataframe(
        one_year_result,
        use_container_width=True,
        hide_index=True
    )


st.divider()


# ==========================================
# 기능 3. 연도 2개 선택 및 비교
# ==========================================

st.header("🔍 3. 두 연도의 기온 비교")

st.write(
    "두 개의 연도를 선택하여 월별 최고기온과 "
    "최저기온이 어떻게 달라졌는지 비교해 보세요."
)

col1, col2 = st.columns(2)

with col1:

    year1 = st.selectbox(
        "첫 번째 연도",
        years,
        index=max(0, len(years) - 2),
        key="compare_year1"
    )

with col2:

    year2 = st.selectbox(
        "두 번째 연도",
        years,
        index=len(years) - 1,
        key="compare_year2"
    )

if year1 == year2:

    st.warning("서로 다른 두 연도를 선택해 주세요.")

else:

    result1 = (
        df[df["연도"] == year1]
        .groupby("월")
        .agg({
            "최고기온(℃)": "max",
            "최저기온(℃)": "min"
        })
        .reindex(all_months)
        .reset_index()
    )

    result2 = (
        df[df["연도"] == year2]
        .groupby("월")
        .agg({
            "최고기온(℃)": "max",
            "최저기온(℃)": "min"
        })
        .reindex(all_months)
        .reset_index()
    )

    fig3 = go.Figure()

    # 첫 번째 연도 최고기온
    fig3.add_trace(
        go.Scatter(
            x=result1["월"],
            y=result1["최고기온(℃)"],
            mode="lines+markers",
            name=f"{year1}년 최고기온",
            line=dict(
                color="hotpink",
                width=3
            )
        )
    )

    # 첫 번째 연도 최저기온
    fig3.add_trace(
        go.Scatter(
            x=result1["월"],
            y=result1["최저기온(℃)"],
            mode="lines+markers",
            name=f"{year1}년 최저기온",
            line=dict(
                color="skyblue",
                width=3
            )
        )
    )

    # 두 번째 연도 최고기온
    fig3.add_trace(
        go.Scatter(
            x=result2["월"],
            y=result2["최고기온(℃)"],
            mode="lines+markers",
            name=f"{year2}년 최고기온",
            line=dict(
                color="deeppink",
                width=3,
                dash="dash"
            )
        )
    )

    # 두 번째 연도 최저기온
    fig3.add_trace(
        go.Scatter(
            x=result2["월"],
            y=result2["최저기온(℃)"],
            mode="lines+markers",
            name=f"{year2}년 최저기온",
            line=dict(
                color="deepskyblue",
                width=3,
                dash="dash"
            )
        )
    )

    make_layout(
        fig3,
        f"{year1}년과 {year2}년 기온 비교"
    )

    st.plotly_chart(
        fig3,
        use_container_width=True
    )

    # 두 연도 데이터 비교표
    st.subheader("📋 두 연도 기온 비교표")

    comparison = pd.DataFrame({
        "월": [
            month_names[m] for m in all_months
        ],
        f"{year1}년 최고기온": result1["최고기온(℃)"],
        f"{year1}년 최저기온": result1["최저기온(℃)"],
        f"{year2}년 최고기온": result2["최고기온(℃)"],
        f"{year2}년 최저기온": result2["최저기온(℃)"]
    })

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )


# ==========================================
# 마지막 안내
# ==========================================

st.divider()

st.success("서울 기온 데이터 분석이 완료되었습니다! 🌡️")

st.caption(
    f"분석 데이터: {csv_path.name} | "
    f"전체 데이터 행 수: {len(df):,}개"
)

