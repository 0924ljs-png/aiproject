
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from statsmodels.tsa.holtwinters import Holt

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="서울 기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 기온 분석 및 미래 예측")
st.markdown(
    "1907년부터 2025년까지의 기온 데이터를 분석하고 "
    "세 가지 알고리즘으로 미래 기온을 예측합니다."
)

# ==========================================
# 2. CSV 파일 찾기
# ==========================================

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
    st.info(
        "기온데이터_UTF8.csv 파일을 app.py와 "
        "같은 폴더에 넣어 주세요."
    )
    st.stop()

# ==========================================
# 3. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data(path):

    try:
        data = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(path, encoding="cp949")

    required = [
        "일시",
        "평균기온(℃)"
    ]

    for col in required:
        if col not in data.columns:
            raise ValueError(
                f"CSV 파일에 {col} 열이 없습니다."
            )

    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    # 두 자리 연도를 순서에 따라 복원
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

    data["평균기온(℃)"] = pd.to_numeric(
        data["평균기온(℃)"],
        errors="coerce"
    )

    data = data.dropna(
        subset=["날짜", "평균기온(℃)"]
    ).copy()

    data["연도"] = data["날짜"].dt.year
    data["월"] = data["날짜"].dt.month

    return data


try:
    df = load_data(str(csv_path))

except Exception as e:
    st.error(f"데이터 오류: {e}")
    st.stop()

# 분석 기간 제한
df = df[
    (df["연도"] >= 1907) &
    (df["연도"] <= 2025)
].copy()

if df.empty:
    st.error("1907~2025년 분석 데이터가 없습니다.")
    st.stop()

# ==========================================
# 4. 월 선택
# ==========================================

month_names = {
    1: "1월", 2: "2월", 3: "3월",
    4: "4월", 5: "5월", 6: "6월",
    7: "7월", 8: "8월", 9: "9월",
    10: "10월", 11: "11월", 12: "12월"
}

st.header("📅 분석할 월 선택")

selected_month = st.selectbox(
    "분석하고 싶은 월을 선택하세요.",
    list(range(1, 13)),
    format_func=lambda x: month_names[x]
)

# 선택 월 데이터
monthly_df = df[
    df["월"] == selected_month
].copy()

# 연도별 평균기온
yearly = (
    monthly_df.groupby("연도")["평균기온(℃)"]
    .mean()
    .sort_index()
)

# 1907~2025년 전체 연도
all_years = np.arange(1907, 2026)

yearly = yearly.reindex(all_years)

# 예측 모델 학습을 위한 결측 연도 보간
filled = yearly.interpolate(
    method="linear",
    limit_direction="both"
)

if filled.isna().any() or len(filled) < 10:
    st.error("예측에 필요한 기온 데이터가 부족합니다.")
    st.stop()

# ==========================================
# 5. 과거 기온 그래프
# ==========================================

st.header(
    f"📈 {month_names[selected_month]} 과거 평균기온 변화"
)

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=yearly.index,
        y=yearly.values,
        mode="lines+markers",
        name="실제 평균기온",
        line=dict(
            color="royalblue",
            width=2
        ),
        marker=dict(size=5)
    )
)

fig1.update_layout(
    title=f"1907~2025년 {month_names[selected_month]} 평균기온",
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    template="plotly_white",
    hovermode="x unified",
    height=500
)

fig1.update_xaxes(
    range=[1907, 2025],
    dtick=10
)

st.plotly_chart(
    fig1,
    use_container_width=True
)

st.caption(
    "실제 관측값이 없는 연도는 과거 기온 그래프에 "
    "표시하지 않습니다."
)

# ==========================================
# 6. 예측 연도 입력
# ==========================================

st.divider()

st.header("🔮 미래 평균기온 예측")

forecast_year = st.number_input(
    "예측하고 싶은 마지막 연도를 입력하세요.",
    min_value=2026,
    max_value=2100,
    value=2035,
    step=1
)

forecast_year = int(forecast_year)

future_years = np.arange(
    2026,
    forecast_year + 1
)

X = all_years.reshape(-1, 1)
y = filled.values

# ==========================================
# 7. 알고리즘 1 : 선형 회귀
# ==========================================

linear_model = LinearRegression()

linear_model.fit(X, y)

linear_prediction = linear_model.predict(
    future_years.reshape(-1, 1)
)

# ==========================================
# 8. 알고리즘 2 : 다항 회귀
# ==========================================

polynomial_model = make_pipeline(
    PolynomialFeatures(degree=2),
    LinearRegression()
)

polynomial_model.fit(X, y)

polynomial_prediction = polynomial_model.predict(
    future_years.reshape(-1, 1)
)

# ==========================================
# 9. 알고리즘 3 : 홀트 선형 추세법
# ==========================================

holt_model = Holt(
    y,
    damped_trend=True,
    initialization_method="estimated"
)

holt_result = holt_model.fit(
    optimized=True
)

holt_prediction = holt_result.forecast(
    len(future_years)
)

# ==========================================
# 10. 세 알고리즘 비교 그래프
# ==========================================

st.subheader("📊 세 가지 예측 알고리즘 비교")

fig2 = go.Figure()

# 실제 데이터
fig2.add_trace(
    go.Scatter(
        x=all_years,
        y=yearly.values,
        mode="lines",
        name="실제 평균기온",
        line=dict(
            color="black",
            width=2
        )
    )
)

# 선형 회귀
fig2.add_trace(
    go.Scatter(
        x=future_years,
        y=linear_prediction,
        mode="lines+markers",
        name="① 선형 회귀",
        line=dict(
            color="hotpink",
            width=3
        ),
        marker=dict(size=5)
    )
)

# 다항 회귀
fig2.add_trace(
    go.Scatter(
        x=future_years,
        y=polynomial_prediction,
        mode="lines+markers",
        name="② 다항 회귀",
        line=dict(
            color="royalblue",
            width=3,
            dash="dash"
        ),
        marker=dict(size=5)
    )
)

# 홀트 선형 추세법
fig2.add_trace(
    go.Scatter(
        x=future_years,
        y=holt_prediction,
        mode="lines+markers",
        name="③ 홀트 선형 추세법",
        line=dict(
            color="green",
            width=3,
            dash="dot"
        ),
        marker=dict(size=5)
    )
)

# 과거와 미래 구분선
fig2.add_vline(
    x=2025,
    line_dash="dash",
    line_color="gray",
    annotation_text="예측 시작",
    annotation_position="top"
)

# 그래프 안에 알고리즘 설명
fig2.add_annotation(
    x=0.02,
    y=0.98,
    xref="paper",
    yref="paper",
    text=(
        "① 선형 회귀: 전체 데이터를 직선으로 학습"
        "<br>② 다항 회귀: 곡선으로 변화 패턴 학습"
        "<br>③ 홀트: 최근 수준과 추세를 반영"
    ),
    showarrow=False,
    align="left",
    bgcolor="rgba(255,255,255,0.9)",
    bordercolor="gray",
    borderwidth=1,
    xanchor="left",
    yanchor="top"
)

fig2.update_layout(
    title=(
        f"{month_names[selected_month]} "
        f"평균기온 미래 예측 비교"
    ),
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    legend_title="예측 알고리즘",
    template="plotly_white",
    hovermode="x unified",
    height=650
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ==========================================
# 11. 알고리즘별 상세 설명
# ==========================================

st.divider()

st.header("📚 예측 알고리즘 알아보기")

with st.expander("① 선형 회귀 (Linear Regression)"):

    st.write(
        "과거의 평균기온과 연도 사이의 관계를 "
        "직선으로 나타내는 방법입니다."
    )

    st.write(
        "기온이 장기적으로 일정하게 상승하거나 "
        "하락하는 경향이 있을 때 이해하기 쉽습니다."
    )

    st.latex("y = ax + b")

    st.info(
        "그래프 특징: 미래 구간이 직선으로 이어집니다."
    )

with st.expander("② 다항 회귀 (Polynomial Regression)"):

    st.write(
        "연도와 기온 사이의 관계를 곡선으로 "
        "표현하는 방법입니다."
    )

    st.write(
        "이 프로그램은 2차 다항식을 사용하여 "
        "곡선 형태의 장기 변화 추세를 학습합니다."
    )

    st.latex("y = ax^2 + bx + c")

    st.info(
        "그래프 특징: 미래 구간이 휘어진 곡선으로 나타납니다."
    )

with st.expander("③ 홀트 선형 추세법 (Holt's Method)"):

    st.write(
        "최근 기온에 더 큰 가중치를 주면서 "
        "현재 수준과 변화 추세를 함께 계산합니다."
    )

    st.write(
        "추세가 계속 이어지지만 시간이 지날수록 "
        "변화 폭이 줄어드는 감쇠 추세를 사용합니다."
    )

    st.latex(
        "L_t = \\alpha Y_t + (1-\\alpha)(L_{t-1}+\\phi T_{t-1})"
    )

    st.info(
        "그래프 특징: 최근 데이터의 수준과 추세를 반영하여 "
        "미래 구간을 예측합니다."
    )

# ==========================================
# 12. 예측 결과 비교표
# ==========================================

st.divider()

st.header("📋 예측 결과 비교표")

comparison_df = pd.DataFrame({
    "연도": future_years,
    "선형 회귀(℃)": linear_prediction,
    "다항 회귀(℃)": polynomial_prediction,
    "홀트 추세법(℃)": np.asarray(holt_prediction)
})

st.dataframe(
    comparison_df.round(2),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 13. 최종 예측값
# ==========================================

st.subheader(
    f"🎯 {forecast_year}년 {month_names[selected_month]} 예측 결과"
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "선형 회귀",
        f"{linear_prediction[-1]:.2f} ℃"
    )

with col2:
    st.metric(
        "다항 회귀",
        f"{polynomial_prediction[-1]:.2f} ℃"
    )

with col3:
    st.metric(
        "홀트 선형 추세법",
        f"{holt_prediction[-1]:.2f} ℃"
    )

# ==========================================
# 14. CSV 다운로드
# ==========================================

csv_data = comparison_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    label="📥 예측 결과 CSV 다운로드",
    data=csv_data,
    file_name=f"{selected_month}월_기온예측.csv",
    mime="text/csv"
)

st.divider()

st.warning(
    "주의: 이 결과는 과거 기온 패턴을 이용한 통계적 예측입니다. "
    "실제 미래 기온이나 기후변화를 확정적으로 예측하는 것은 아닙니다. "
    "장기 예측일수록 불확실성이 커질 수 있습니다."
)

st.success("서울 월별 기온 분석 및 예측이 완료되었습니다! 🌡️")
