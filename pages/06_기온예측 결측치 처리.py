
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from pathlib import Path
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="서울 기온 분석 및 예측",
    page_icon="🌡️",
    layout="wide"
)

st.title("🌡️ 서울 월별 기온 분석 및 미래 예측")
st.write(
    "과거 기온을 분석하고 결측치 처리 방법과 "
    "예측 알고리즘에 따른 미래 기온 차이를 알아보세요."
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
    folder / "data" / "기온데이터_UTF8.csv"
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
        data = pd.read_csv(path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        data = pd.read_csv(path, encoding="cp949")

    required = ["일시", "평균기온(℃)"]

    for col in required:
        if col not in data.columns:
            raise ValueError(f"{col} 열이 없습니다.")

    month_dict = {
        "Jan": 1, "Feb": 2, "Mar": 3,
        "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9,
        "Oct": 10, "Nov": 11, "Dec": 12
    }

    dates = []
    century = 1900
    previous_year = None

    for value in data["일시"].astype(str).str.strip():

        try:
            month_text, year_text = value.split("-")
            month = month_dict[month_text]
            year = int(year_text)

            # 99년에서 00년으로 넘어갈 때 세기 변경
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

    data = data.dropna(subset=["날짜"]).copy()

    data["연도"] = data["날짜"].dt.year
    data["월"] = data["날짜"].dt.month

    return data


try:
    df = load_data(str(csv_path))
except Exception as e:
    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()

df = df[
    (df["연도"] >= 1907) &
    (df["연도"] <= 2025)
].copy()

if df.empty:
    st.error("분석할 데이터가 없습니다.")
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
    "분석할 월을 선택하세요.",
    range(1, 13),
    format_func=lambda x: month_names[x]
)

# 연도별 월평균 기온
monthly_df = df[df["월"] == selected_month]

yearly = (
    monthly_df.groupby("연도")["평균기온(℃)"]
    .mean()
    .reindex(range(1907, 2026))
)

years_all = np.arange(1907, 2026)

# ==========================================
# 5. 과거 실제 기온 그래프
# ==========================================

st.header("📈 과거 평균기온 분석")

fig1 = go.Figure()

fig1.add_trace(
    go.Scatter(
        x=years_all,
        y=yearly.values,
        mode="lines+markers",
        name="실제 평균기온",
        connectgaps=False,
        line=dict(color="royalblue", width=2)
    )
)

fig1.update_layout(
    title=f"1907~2025년 {month_names[selected_month]} 평균기온",
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    template="plotly_white",
    height=450
)

st.plotly_chart(fig1, use_container_width=True)

# ==========================================
# 6. 결측치 처리 방법 선택
# ==========================================

st.divider()

st.header("🧩 결측치 처리 방법 선택")

st.write(
    "결측치를 어떤 방식으로 처리하느냐에 따라 "
    "예측 결과가 어떻게 달라지는지 확인해 보세요."
)

missing_method = st.radio(
    "결측치 처리 방법을 선택하세요.",
    [
        "1. 결측치 제거",
        "2. 중앙값으로 대체",
        "3. 선형보간법"
    ],
    horizontal=True
)

# 선택 월의 연도별 데이터
raw_series = yearly.copy()

missing_count = int(raw_series.isna().sum())

st.metric(
    "선택한 월의 결측 연도 수",
    f"{missing_count}개"
)

# 결측치 처리 함수
def process_missing(series, method):

    result = series.copy()

    if method == "1. 결측치 제거":
        result = result.dropna()

    elif method == "2. 중앙값으로 대체":
        median_value = result.median()
        result = result.fillna(median_value)

    elif method == "3. 선형보간법":
        result = result.interpolate(
            method="linear",
            limit_direction="both"
        )

    return result


processed_series = process_missing(
    raw_series,
    missing_method
)

if len(processed_series) < 3:
    st.error("예측에 필요한 데이터가 부족합니다.")
    st.stop()

if processed_series.isna().any():
    st.error("결측치 처리 후에도 빈 데이터가 남아 있습니다.")
    st.stop()

# 결측치 처리 결과 확인
st.subheader("결측치 처리 결과")

missing_comparison = pd.DataFrame({
    "원래 평균기온": raw_series,
    "처리 후 평균기온": processed_series.reindex(years_all)
})

st.dataframe(
    missing_comparison.style.format("{:.2f}"),
    use_container_width=True
)

# ==========================================
# 7. 미래 예측 연도
# ==========================================

st.divider()

st.header("🔮 미래 평균기온 예측")

forecast_year = st.number_input(
    "예측하고 싶은 마지막 연도",
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

# ==========================================
# 8. 예측 알고리즘 함수
# ==========================================

def predict_temperature(series, algorithm, future_years):

    train_years = series.index.to_numpy(dtype=float)
    train_values = series.to_numpy(dtype=float)

    future_x = np.asarray(
        future_years,
        dtype=float
    ).reshape(-1, 1)

    # 선형 회귀
    if algorithm == "선형 회귀":

        model = LinearRegression()

        model.fit(
            train_years.reshape(-1, 1),
            train_values
        )

        return model.predict(future_x)

    # 다항 회귀
    elif algorithm == "다항 회귀":

        model = make_pipeline(
            PolynomialFeatures(degree=2),
            LinearRegression()
        )

        model.fit(
            train_years.reshape(-1, 1),
            train_values
        )

        return model.predict(future_x)

    # 홀트 감쇠 선형 추세법
    elif algorithm == "홀트 선형 추세법":

        # 실제 연도 간격을 반영하는 홀트 추세 계산
        # 결측치 제거 시에도 연도 간격이 유지됨

        phi = 0.98

        def geometric_sum(n):
            return phi * (1 - phi ** n) / (1 - phi)

        def run_holt(alpha, beta):

            level = train_values[0]

            if len(train_values) >= 2:
                gap = train_years[1] - train_years[0]
                trend = (
                    (train_values[1] - train_values[0]) / gap
                )
            else:
                trend = 0

            errors = []

            for i in range(1, len(train_values)):

                gap = train_years[i] - train_years[i - 1]

                predicted = (
                    level + trend * geometric_sum(gap)
                )

                errors.append(
                    (train_values[i] - predicted) ** 2
                )

                old_level = level
                old_trend = trend

                level = (
                    alpha * train_values[i]
                    + (1 - alpha) * predicted
                )

                trend = (
                    beta * ((level - old_level) / gap)
                    + (1 - beta) * old_trend
                )

            return level, trend, np.mean(errors)

        best_error = float("inf")
        best_level = None
        best_trend = None

        for alpha in np.arange(0.1, 1.0, 0.1):
            for beta in np.arange(0.1, 1.0, 0.1):

                level, trend, error = run_holt(
                    alpha, beta
                )

                if error < best_error:
                    best_error = error
                    best_level = level
                    best_trend = trend

        predictions = []

        last_year = train_years[-1]

        for year in future_years:

            gap = int(year - last_year)

            predictions.append(
                best_level
                + best_trend * geometric_sum(gap)
            )

        return np.array(predictions)

# ==========================================
# 9. 알고리즘 선택
# ==========================================

st.subheader("🤖 예측 알고리즘 선택")

algorithms = [
    "선형 회귀",
    "다항 회귀",
    "홀트 선형 추세법"
]

selected_algorithms = st.multiselect(
    "비교하고 싶은 알고리즘을 선택하세요.",
    algorithms,
    default=algorithms
)

if not selected_algorithms:
    st.warning("최소 한 개의 알고리즘을 선택해 주세요.")
    st.stop()

# 알고리즘 색상
algorithm_colors = {
    "선형 회귀": "hotpink",
    "다항 회귀": "royalblue",
    "홀트 선형 추세법": "green"
}

# ==========================================
# 10. 선택한 결측치 처리 + 알고리즘 예측
# ==========================================

st.header("📊 선택한 조건에 따른 미래 예측")

fig2 = go.Figure()

# 과거 실제 기온
fig2.add_trace(
    go.Scatter(
        x=years_all,
        y=yearly.values,
        mode="lines",
        name="실제 평균기온",
        line=dict(color="black", width=2)
    )
)

# 결측치 처리 후 학습 데이터
fig2.add_trace(
    go.Scatter(
        x=processed_series.index,
        y=processed_series.values,
        mode="markers",
        name="처리 후 학습 데이터",
        marker=dict(
            color="gray",
            size=5,
            symbol="circle-open"
        )
    )
)

prediction_results = {}

for algorithm in selected_algorithms:

    prediction = predict_temperature(
        processed_series,
        algorithm,
        future_years
    )

    prediction_results[algorithm] = prediction

    fig2.add_trace(
        go.Scatter(
            x=future_years,
            y=prediction,
            mode="lines+markers",
            name=algorithm,
            line=dict(
                color=algorithm_colors[algorithm],
                width=3
            )
        )
    )

fig2.add_vline(
    x=2025,
    line_dash="dash",
    line_color="gray",
    annotation_text="예측 시작"
)

fig2.update_layout(
    title=(
        f"{month_names[selected_month]} "
        f"결측치 처리 및 미래 기온 예측"
    ),
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    legend_title="범례",
    hovermode="x unified",
    template="plotly_white",
    height=600
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# ==========================================
# 11. 결측치 처리 방식별 예측 차이
# ==========================================

st.divider()

st.header("🔬 결측치 처리 방법에 따른 예측 결과 비교")

st.write(
    "동일한 알고리즘을 사용하면서 결측치 처리 방법만 바꾸면 "
    "미래 기온 예측이 어떻게 달라지는지 비교합니다."
)

comparison_algorithm = st.selectbox(
    "비교할 예측 알고리즘",
    algorithms,
    key="missing_comparison_algorithm"
)

methods = [
    "1. 결측치 제거",
    "2. 중앙값으로 대체",
    "3. 선형보간법"
]

method_colors = {
    "1. 결측치 제거": "hotpink",
    "2. 중앙값으로 대체": "royalblue",
    "3. 선형보간법": "green"
}

fig3 = go.Figure()

fig3.add_trace(
    go.Scatter(
        x=years_all,
        y=yearly.values,
        mode="lines",
        name="실제 평균기온",
        line=dict(color="black", width=2)
    )
)

missing_predictions = {}

for method in methods:

    temp_series = process_missing(
        raw_series,
        method
    )

    if len(temp_series) < 3 or temp_series.isna().any():
        continue

    prediction = predict_temperature(
        temp_series,
        comparison_algorithm,
        future_years
    )

    missing_predictions[method] = prediction

    fig3.add_trace(
        go.Scatter(
            x=future_years,
            y=prediction,
            mode="lines+markers",
            name=method,
            line=dict(
                color=method_colors[method],
                width=3
            )
        )
    )

fig3.add_vline(
    x=2025,
    line_dash="dash",
    line_color="gray"
)

fig3.update_layout(
    title=(
        f"{comparison_algorithm}: "
        "결측치 처리 방식별 예측 비교"
    ),
    xaxis_title="연도",
    yaxis_title="평균기온(℃)",
    legend_title="결측치 처리 방법",
    hovermode="x unified",
    template="plotly_white",
    height=600
)

st.plotly_chart(
    fig3,
    use_container_width=True
)

# ==========================================
# 12. 알고리즘별 설명
# ==========================================

st.divider()

st.header("📚 예측 알고리즘 알아보기")

with st.expander("① 선형 회귀"):

    st.write(
        "과거 연도와 평균기온의 관계를 직선으로 학습합니다."
    )

    st.latex("y = ax + b")

    st.info(
        "그래프 특징: 일정한 상승 또는 하락 추세를 "
        "직선으로 표현합니다."
    )

with st.expander("② 다항 회귀"):

    st.write(
        "과거 기온의 변화를 곡선으로 학습합니다. "
        "이 프로그램에서는 2차 다항식을 사용합니다."
    )

    st.latex("y = ax^2 + bx + c")

    st.info(
        "그래프 특징: 기온 변화의 곡선 형태를 표현합니다."
    )

with st.expander("③ 홀트 선형 추세법"):

    st.write(
        "최근 관측값을 반영하여 기온의 현재 수준과 "
        "변화 추세를 함께 계산합니다."
    )

    st.info(
        "그래프 특징: 최근 변화와 추세의 지속성을 반영하며 "
        "감쇠 추세를 적용합니다."
    )

# ==========================================
# 13. 예측 결과 표
# ==========================================

st.divider()

st.header("📋 예측 결과 비교표")

result_df = pd.DataFrame({
    "연도": future_years
})

for algorithm, values in prediction_results.items():
    result_df[algorithm + "(℃)"] = values

st.dataframe(
    result_df.round(2),
    use_container_width=True,
    hide_index=True
)

# 결측치 처리별 최종 예측 비교표
st.subheader("결측치 처리별 최종 예측값")

final_values = []

for method, values in missing_predictions.items():

    final_values.append({
        "결측치 처리 방법": method,
        "예측 알고리즘": comparison_algorithm,
        "예측 연도": forecast_year,
        "예측 평균기온(℃)": round(float(values[-1]), 2)
    })

st.dataframe(
    pd.DataFrame(final_values),
    use_container_width=True,
    hide_index=True
)

# ==========================================
# 14. CSV 다운로드
# ==========================================

csv_data = result_df.to_csv(
    index=False
).encode("utf-8-sig")

st.download_button(
    "📥 예측 결과 CSV 다운로드",
    data=csv_data,
    file_name="서울_기온_예측결과.csv",
    mime="text/csv"
)

st.warning(
    "미래 기온은 과거 자료를 이용한 통계적 추정치입니다. "
    "실제 기상 예보나 확정적인 기후 전망은 아닙니다."
)

st.success("서울 기온 분석 및 예측이 완료되었습니다! 🌡️")
