
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from pathlib import Path
from io import BytesIO

# =====================================
# 1. 페이지 설정
# =====================================

st.set_page_config(
    page_title="서울시 연령별 인구 분석",
    page_icon="🌸",
    layout="wide"
)

st.title("🌸 서울시 연령별 인구 분석")

st.markdown(
    "행정구역, 성별, 연도를 선택하여 "
    "연령별 인구를 그래프로 확인해 보세요!"
)

# =====================================
# 2. CSV 파일 불러오기
# =====================================

@st.cache_data
def load_data(file_bytes):

    encodings = [
        "euc-kr",
        "cp949",
        "utf-8-sig",
        "utf-8"
    ]

    df = None

    for encoding in encodings:
        try:
            df = pd.read_csv(
                BytesIO(file_bytes),
                encoding=encoding
            )
            break

        except UnicodeDecodeError:
            continue

    if df is None:
        raise ValueError(
            "CSV 인코딩을 읽을 수 없습니다."
        )

    # 행정구역 열 확인
    if "행정구역" not in df.columns:
        raise ValueError(
            "'행정구역' 열을 찾을 수 없습니다."
        )

    # 행정구역 이름 정리
    df["행정구역명"] = (
        df["행정구역"]
        .astype(str)
        .str.replace(
            r"\s*\(\d+\)\s*$",
            "",
            regex=True
        )
        .str.strip()
    )

    # 인구 데이터 숫자 변환
    for col in df.columns:

        if col not in ["행정구역", "행정구역명"]:

            df[col] = pd.to_numeric(
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.strip(),
                errors="coerce"
            )

    return df


# =====================================
# 3. CSV 파일 경로 설정
# =====================================

# 현재 파일은 pages 폴더 안에 있음
# CSV 파일은 pages의 상위 폴더에 있음

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "population.csv"

uploaded_file = st.file_uploader(
    "📂 population.csv 파일 업로드",
    type=["csv"]
)

try:

    if uploaded_file is not None:

        file_bytes = uploaded_file.getvalue()

    elif CSV_PATH.exists():

        file_bytes = CSV_PATH.read_bytes()

    else:

        st.error(
            "population.csv 파일을 찾을 수 없습니다."
        )

        st.info(
            "population.csv 파일을 "
            "app.py와 같은 상위 폴더에 넣어 주세요."
        )

        st.stop()

    df = load_data(file_bytes)

except Exception as e:

    st.error(f"데이터 불러오기 오류: {e}")
    st.stop()


# =====================================
# 4. 연도와 연령대 찾기
# =====================================

years = sorted(set(
    int(match.group(1))
    for col in df.columns
    if (match := re.match(
        r"^(\d{4})년_",
        str(col)
    ))
))

age_groups = []

for col in df.columns:

    match = re.match(
        r"^\d{4}년_.*_거주자_(\d+~\d+세|100세 이상)$",
        str(col)
    )

    if match:
        age_groups.append(match.group(1))

age_groups = list(dict.fromkeys(age_groups))

if not years or not age_groups:

    st.error(
        "연도 또는 연령대 데이터를 찾을 수 없습니다. "
        "CSV 파일의 열 이름을 확인해 주세요."
    )

    st.stop()


# =====================================
# 5. 행정구역, 성별, 연도 선택
# =====================================

st.subheader("🔎 분석 조건 선택")

col1, col2, col3 = st.columns(3)

districts = sorted(
    df["행정구역명"].dropna().unique().tolist()
)

with col1:

    selected_district = st.selectbox(
        "🏙️ 행정구역 선택",
        districts
    )

with col2:

    selected_sex = st.selectbox(
        "👥 성별 선택",
        ["전체", "남성", "여성"]
    )

with col3:

    selected_year = st.selectbox(
        "📅 연도 선택",
        years,
        index=len(years) - 1
    )


# =====================================
# 6. 선택 조건에 맞는 데이터 추출
# =====================================

sex_key = {
    "전체": "",
    "남성": "남",
    "여성": "여"
}

sex = sex_key[selected_sex]

selected_data = df[
    df["행정구역명"] == selected_district
]

if selected_data.empty:

    st.error("선택한 행정구역의 데이터가 없습니다.")
    st.stop()

row = selected_data.iloc[0]

population_values = []

for age in age_groups:

    if sex == "":

        column_name = (
            f"{selected_year}년_거주자_{age}"
        )

    else:

        column_name = (
            f"{selected_year}년_{sex}_거주자_{age}"
        )

    if column_name in df.columns:

        value = row[column_name]

        if pd.isna(value):
            value = 0

        population_values.append(int(value))

    else:

        population_values.append(0)


# =====================================
# 7. 그래프 데이터 만들기
# =====================================

chart_df = pd.DataFrame({

    "나이": age_groups,

    "인구수": population_values

})

total_population = sum(population_values)


# =====================================
# 8. 인구 합계 표시
# =====================================

st.divider()

st.metric(
    label=(
        f"{selected_year}년 "
        f"{selected_district} "
        f"{selected_sex} 인구 합계"
    ),

    value=f"{total_population:,}명"
)


# =====================================
# 9. 핫핑크 꺾은선 그래프
# =====================================

st.subheader("📈 연령별 인구 꺾은선 그래프")

fig = go.Figure()

fig.add_trace(

    go.Scatter(

        x=chart_df["나이"],

        y=chart_df["인구수"],

        mode="lines+markers",

        name="인구수",

        line=dict(
            color="#FF1493",
            width=4
        ),

        marker=dict(
            color="#FF1493",
            size=9
        ),

        hovertemplate=(
            "나이: %{x}<br>"
            "인구수: %{y:,.0f}명"
            "<extra></extra>"
        )

    )

)


# =====================================
# 10. 그래프 디자인
# =====================================

fig.update_layout(

    title=(
        f"{selected_district} "
        f"{selected_year}년 "
        f"{selected_sex} 연령별 인구"
    ),

    xaxis_title="나이",

    yaxis_title="인구수(명)",

    template="plotly_white",

    height=600,

    hovermode="x unified",

    font=dict(
        family="Arial, sans-serif",
        size=13
    ),

    margin=dict(
        l=30,
        r=30,
        t=80,
        b=50
    )

)


# =====================================
# 11. 가로축 설정
# 10살 단위 연령 구분
# =====================================

fig.update_xaxes(

    type="category",

    categoryorder="array",

    categoryarray=age_groups,

    tickmode="array",

    tickvals=age_groups,

    ticktext=age_groups,

    showgrid=True,

    gridcolor="#E8DCE3",

    gridwidth=1

)


# =====================================
# 12. 세로축 설정
# 1000만 명 단위 구분
# =====================================

max_population = max(population_values) if population_values else 0

y_max = max(
    10_000_000,
    ((max_population // 10_000_000) + 1)
    * 10_000_000
)

fig.update_yaxes(

    range=[0, y_max],

    tickmode="linear",

    tick0=0,

    dtick=10_000_000,

    tickformat=",",

    showgrid=True,

    gridcolor="#E8DCE3",

    gridwidth=1

)


# =====================================
# 13. 그래프 출력
# =====================================

st.plotly_chart(
    fig,
    use_container_width=True
)


# =====================================
# 14. 데이터 표 출력
# =====================================

with st.expander("📋 연령별 인구 데이터 확인"):

    display_df = chart_df.copy()

    display_df["인구수"] = (
        display_df["인구수"]
        .map(lambda x: f"{x:,}명")
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )


# =====================================
# 15. 마무리 안내
# =====================================

st.divider()

st.markdown(
    """
    🌸 **서울시 인구 분석 결과**

    - 행정구역별 인구 비교
    - 남녀 인구 비교
    - 연령별 인구 분포
    - 연도별 인구 변화

    원하는 조건을 선택해서
    서울시의 인구 구조를 살펴보세요!
    """
)

st.caption(
    "데이터 출처: 제공된 population.csv"
)
