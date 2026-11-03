
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# 1. 페이지 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="세계 국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

# --------------------------------------------------
# 2. CSV 데이터 불러오기
# --------------------------------------------------
DATA_FILE = Path(__file__).parent / "countriesMBTI_16types.csv"


@st.cache_data
def load_data(file_path):

    data = pd.read_csv(file_path)

    if "Country" not in data.columns:
        raise ValueError("CSV 파일에 Country 열이 없습니다.")

    mbti_columns = [
        column for column in data.columns
        if column != "Country"
    ]

    if len(mbti_columns) != 16:
        raise ValueError(
            f"MBTI 열은 16개여야 합니다. 현재 {len(mbti_columns)}개입니다."
        )

    data["Country"] = data["Country"].astype(str).str.strip()

    data = data.dropna(subset=["Country"])
    data = data.drop_duplicates(
        subset=["Country"],
        keep="first"
    )

    for column in mbti_columns:
        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    data[mbti_columns] = data[mbti_columns].fillna(0)

    return data, mbti_columns


# --------------------------------------------------
# 3. 앱 제목
# --------------------------------------------------
st.title("🌍 세계 국가별 MBTI 분석")

st.markdown("""
### 국가별 MBTI 성격 유형을 한눈에 비교해 보세요!

158개 국가의 MBTI 16가지 유형별 비율을
막대그래프로 확인할 수 있습니다.
""")

# --------------------------------------------------
# 4. 데이터 로딩 오류 처리
# --------------------------------------------------
try:

    df, mbti_columns = load_data(DATA_FILE)

except FileNotFoundError:

    st.error(
        "CSV 파일을 찾을 수 없습니다. "
        "countriesMBTI_16types.csv 파일을 "
        "app.py와 같은 폴더에 넣어 주세요."
    )

    st.stop()

except Exception as error:

    st.error(f"데이터 오류: {error}")

    st.stop()


# --------------------------------------------------
# 5. 국가 선택
# --------------------------------------------------
countries = sorted(
    df["Country"].unique().tolist()
)

selected_country = st.selectbox(
    "🗺️ 분석할 국가를 선택하세요.",
    countries,
    index=0
)


# --------------------------------------------------
# 6. 선택한 국가의 MBTI 데이터 추출
# --------------------------------------------------
country_data = df.loc[
    df["Country"] == selected_country,
    mbti_columns
].iloc[0]


# --------------------------------------------------
# 7. MBTI 비율 높은 순서대로 정렬
# --------------------------------------------------
chart_data = (
    country_data
    .rename_axis("MBTI")
    .reset_index(name="Ratio")
    .sort_values(
        "Ratio",
        ascending=False
    )
    .reset_index(drop=True)
)

# 소수 데이터를 백분율로 변환
chart_data["Percentage"] = (
    chart_data["Ratio"] * 100
)


# --------------------------------------------------
# 8. 색상 변환 함수
# --------------------------------------------------
def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):

    return "#{:02X}{:02X}{:02X}".format(*rgb)


def interpolate_color(
    start_color,
    end_color,
    amount
):

    start = hex_to_rgb(start_color)
    end = hex_to_rgb(end_color)

    rgb = tuple(
        round(
            start[i] +
            (end[i] - start[i]) * amount
        )
        for i in range(3)
    )

    return rgb_to_hex(rgb)


# --------------------------------------------------
# 9. 막대그래프 색상 지정
# --------------------------------------------------
colors = []

# 1위는 빨간색
colors.append("#E53935")

# 나머지는 파란색 그라데이션
blue_start = "#1557A0"
blue_end = "#DCEBFF"

remaining_count = len(chart_data) - 1

for i in range(remaining_count):

    amount = i / max(remaining_count - 1, 1)

    color = interpolate_color(
        blue_start,
        blue_end,
        amount
    )

    colors.append(color)


# --------------------------------------------------
# 10. 가장 높은 MBTI 정보
# --------------------------------------------------
top_mbti = chart_data.iloc[0]["MBTI"]

top_percentage = chart_data.iloc[0]["Percentage"]


# --------------------------------------------------
# 11. 주요 통계 표시
# --------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "🌎 분석 국가",
        selected_country
    )

with col2:

    st.metric(
        "🏆 가장 높은 MBTI",
        top_mbti
    )

with col3:

    st.metric(
        "📊 1위 유형 비율",
        f"{top_percentage:.2f}%"
    )


st.divider()


# --------------------------------------------------
# 12. MBTI 막대그래프 만들기
# --------------------------------------------------
fig = go.Figure(

    go.Bar(

        x=chart_data["Percentage"],

        y=chart_data["MBTI"],

        orientation="h",

        marker=dict(

            color=colors,

            line=dict(
                color="rgba(0,0,0,0.08)",
                width=0.5
            )

        ),

        text=[
            f"{value:.2f}%"
            for value in chart_data["Percentage"]
        ],

        textposition="outside",

        cliponaxis=False,

        hovertemplate=(
            "<b>%{y}</b><br>"
            "비율: %{x:.2f}%"
            "<extra></extra>"
        )

    )

)


# --------------------------------------------------
# 13. 그래프 디자인
# --------------------------------------------------
fig.update_layout(

    title=dict(

        text=(
            f"🇺🇳 {selected_country}의 "
            "MBTI 16가지 유형별 비율"
        ),

        x=0.02,

        xanchor="left"

    ),

    xaxis=dict(

        title="비율 (%)",

        ticksuffix="%",

        showgrid=True,

        gridcolor="rgba(128,128,128,0.18)",

        rangemode="tozero"

    ),

    yaxis=dict(

        title="MBTI 유형",

        autorange="reversed"

    ),

    height=650,

    margin=dict(
        l=30,
        r=70,
        t=80,
        b=50
    ),

    plot_bgcolor="white",

    paper_bgcolor="white",

    font=dict(
        size=13
    ),

    showlegend=False

)


# --------------------------------------------------
# 14. Streamlit 화면에 그래프 출력
# --------------------------------------------------
st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 15. MBTI 순위표
# --------------------------------------------------
st.subheader("🏅 MBTI 유형별 순위")

ranking = chart_data.copy()

ranking.insert(
    0,
    "순위",
    range(1, len(ranking) + 1)
)

ranking["비율"] = ranking["Percentage"].map(
    lambda value: f"{value:.2f}%"
)

ranking = ranking[
    ["순위", "MBTI", "비율"]
]

st.dataframe(
    ranking,
    use_container_width=True,
    hide_index=True
)


# --------------------------------------------------
# 16. 데이터 안내
# --------------------------------------------------
with st.expander("ℹ️ 데이터 이용 안내"):

    st.write("""
    - 업로드한 countriesMBTI_16types.csv 파일을 사용합니다.
    - 원본 데이터의 소수 비율을 백분율로 변환합니다.
    - 조사 연도, 표본 크기 및 조사 방법은 파일에서 확인할 수 없습니다.
    - 따라서 국가 전체 국민의 성격을 단정하는 자료가 아닌
      참고용 데이터로 활용해 주세요.
    """)


# --------------------------------------------------
# 17. 하단 안내
# --------------------------------------------------
st.caption(
    "🌍 세계 국가별 MBTI 분석 | Streamlit으로 제작"
)
