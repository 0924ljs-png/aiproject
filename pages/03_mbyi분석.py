
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import io

# --------------------------------------------------
# 1. 페이지 설정
# --------------------------------------------------
st.set_page_config(
    page_title="세계 국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

# --------------------------------------------------
# 2. 앱 제목
# --------------------------------------------------
st.title("🌍 세계 국가별 MBTI 분석")

st.markdown("""
### 세계 여러 나라의 MBTI 유형을 비교해 보세요!

국가를 선택하면 MBTI 16가지 유형별 비율을
막대그래프로 확인할 수 있습니다.
""")

# --------------------------------------------------
# 3. CSV 파일 자동 검색
# --------------------------------------------------
CSV_FILENAME = "countriesMBTI_16types.csv"

BASE_DIR = Path(__file__).resolve().parent

def find_csv_file():

    # 검색할 폴더
    search_dirs = [
        BASE_DIR,
        BASE_DIR / "data",
        Path.cwd(),
        Path.cwd() / "data"
    ]

    # 중복 폴더 제거
    unique_dirs = list(dict.fromkeys(search_dirs))

    # 먼저 정확한 파일명 검색
    for folder in unique_dirs:

        file_path = folder / CSV_FILENAME

        if file_path.is_file():
            return file_path

    # 대소문자 차이가 있는 파일명도 검색
    for folder in unique_dirs:

        if folder.is_dir():

            for file_path in folder.glob("*.csv"):

                if file_path.name.lower() == CSV_FILENAME.lower():
                    return file_path

    # 하위 폴더까지 검색
    if BASE_DIR.is_dir():

        for file_path in BASE_DIR.rglob("*.csv"):

            if file_path.name.lower() == CSV_FILENAME.lower():
                return file_path

    return None


# --------------------------------------------------
# 4. CSV 데이터 읽기
# --------------------------------------------------
@st.cache_data
def load_data(file_bytes):

    # UTF-8 및 한글 인코딩 대응
    try:
        df = pd.read_csv(
            io.BytesIO(file_bytes),
            encoding="utf-8-sig"
        )

    except UnicodeDecodeError:
        df = pd.read_csv(
            io.BytesIO(file_bytes),
            encoding="cp949"
        )

    # 열 이름 공백 제거
    df.columns = df.columns.astype(str).str.strip()

    # 국가 열 확인
    if "Country" not in df.columns:

        raise ValueError(
            "CSV 파일에 Country 열이 없습니다."
        )

    # MBTI 열 추출
    mbti_columns = [
        col for col in df.columns
        if col != "Country"
    ]

    if len(mbti_columns) != 16:

        raise ValueError(
            f"MBTI 열은 16개여야 합니다. "
            f"현재 {len(mbti_columns)}개입니다."
        )

    # 국가명 정리
    df["Country"] = (
        df["Country"]
        .astype(str)
        .str.strip()
    )

    df = df.dropna(subset=["Country"])

    df = df[
        df["Country"] != ""
    ]

    df = df.drop_duplicates(
        subset=["Country"],
        keep="first"
    )

    # 숫자 데이터 변환
    for col in mbti_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df[mbti_columns] = (
        df[mbti_columns].fillna(0)
    )

    return df, mbti_columns


# --------------------------------------------------
# 5. CSV 파일 불러오기
# --------------------------------------------------
csv_path = find_csv_file()

file_bytes = None

if csv_path is not None:

    try:

        file_bytes = csv_path.read_bytes()

        st.success(
            f"✅ CSV 파일을 찾았습니다: {csv_path.name}"
        )

    except Exception as error:

        st.error(
            f"파일을 읽을 수 없습니다: {error}"
        )

# CSV 파일을 찾지 못한 경우 직접 업로드
if file_bytes is None:

    st.warning(
        "CSV 파일을 자동으로 찾지 못했습니다. "
        "아래에서 CSV 파일을 직접 업로드해 주세요."
    )

    uploaded_file = st.file_uploader(
        "📂 countriesMBTI_16types.csv 업로드",
        type=["csv"]
    )

    if uploaded_file is None:

        st.info("""
        GitHub 저장소에 CSV 파일을 올리거나
        위의 업로드 버튼으로 CSV 파일을 선택해 주세요.
        """)

        st.stop()

    file_bytes = uploaded_file.getvalue()


# --------------------------------------------------
# 6. 데이터 분석
# --------------------------------------------------
try:

    df, mbti_columns = load_data(file_bytes)

except Exception as error:

    st.error(
        f"데이터 분석 중 오류가 발생했습니다: {error}"
    )

    st.stop()


# --------------------------------------------------
# 7. 국가 선택
# --------------------------------------------------
countries = sorted(
    df["Country"].unique().tolist()
)

selected_country = st.selectbox(
    "🗺️ 분석할 국가를 선택하세요.",
    countries
)


# --------------------------------------------------
# 8. 선택 국가 데이터 추출
# --------------------------------------------------
country_data = df.loc[
    df["Country"] == selected_country,
    mbti_columns
].iloc[0]


# --------------------------------------------------
# 9. MBTI 비율 정렬
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

# 백분율 변환
chart_data["Percentage"] = (
    chart_data["Ratio"] * 100
)


# --------------------------------------------------
# 10. 색상 변환 함수
# --------------------------------------------------
def hex_to_rgb(hex_color):

    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):

    return "#{:02X}{:02X}{:02X}".format(
        *rgb
    )


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
# 11. 그래프 색상 지정
# --------------------------------------------------
colors = []

# 1위 빨간색
colors.append("#E53935")

# 나머지 파란색 그라데이션
blue_start = "#1557A0"

blue_end = "#DCEBFF"

remaining_count = len(chart_data) - 1

for i in range(remaining_count):

    amount = (
        i / max(remaining_count - 1, 1)
    )

    color = interpolate_color(
        blue_start,
        blue_end,
        amount
    )

    colors.append(color)


# --------------------------------------------------
# 12. 1위 MBTI 확인
# --------------------------------------------------
top_mbti = chart_data.iloc[0]["MBTI"]

top_percentage = chart_data.iloc[0]["Percentage"]


# --------------------------------------------------
# 13. 주요 통계 표시
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
# 14. 막대그래프 생성
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
# 15. 그래프 디자인
# --------------------------------------------------
fig.update_layout(

    title=dict(

        text=(
            f"🌍 {selected_country}의 "
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

    font=dict(size=13),

    showlegend=False

)


# --------------------------------------------------
# 16. 그래프 화면 출력
# --------------------------------------------------
st.plotly_chart(
    fig,
    use_container_width=True
)


# --------------------------------------------------
# 17. MBTI 순위표
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
# 18. 데이터 안내
# --------------------------------------------------
with st.expander("ℹ️ 데이터 이용 안내"):

    st.write("""
    - 업로드한 CSV 파일을 바탕으로 분석합니다.
    - 원본 소수 데이터를 백분율로 변환합니다.
    - 조사 연도와 표본 크기는 제공된 CSV에서 확인할 수 없습니다.
    - 국가별 MBTI 비율은 참고용 자료이며,
      국가 구성원 전체의 성격을 단정하지 않습니다.
    """)


# --------------------------------------------------
# 19. 하단 안내
# --------------------------------------------------
st.caption(
    "🌍 세계 국가별 MBTI 분석 | Streamlit 제작"
)
