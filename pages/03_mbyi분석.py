
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
import io

# 1. 페이지 설정
st.set_page_config(
    page_title="세계 국가별 MBTI 분석",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 세계 국가별 MBTI 분석")
st.write("국가별 MBTI 분포와 MBTI 유형별 국가 순위를 확인해 보세요.")

# 2. CSV 파일 찾기
CSV_FILENAME = "countriesMBTI_16types.csv"
BASE_DIR = Path(__file__).resolve().parent


def find_csv_file():
    search_dirs = [
        BASE_DIR,
        BASE_DIR / "data",
        Path.cwd(),
        Path.cwd() / "data"
    ]

    checked = set()

    for folder in search_dirs:
        folder = folder.resolve()

        if folder in checked:
            continue

        checked.add(folder)

        candidate = folder / CSV_FILENAME

        if candidate.is_file():
            return candidate

    if BASE_DIR.is_dir():
        for candidate in BASE_DIR.rglob("*.csv"):
            if candidate.name.lower() == CSV_FILENAME.lower():
                return candidate

    return None


# 3. CSV 데이터 읽기
@st.cache_data
def load_data(file_bytes):

    last_error = None

    for encoding in ("utf-8-sig", "cp949", "latin1"):
        try:
            df = pd.read_csv(
                io.BytesIO(file_bytes),
                encoding=encoding
            )
            break

        except UnicodeDecodeError as error:
            last_error = error

    else:
        raise ValueError(
            f"CSV 인코딩 오류: {last_error}"
        )

    df.columns = df.columns.astype(str).str.strip()

    if "Country" not in df.columns:
        raise ValueError(
            "CSV 파일에 Country 열이 없습니다."
        )

    expected_mbti = {
        "ISTJ", "ISFJ", "INFJ", "INTJ",
        "ISTP", "ISFP", "INFP", "INTP",
        "ESTP", "ESFP", "ENFP", "ENTP",
        "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    }

    mbti_columns = [
        col for col in df.columns
        if col.strip().upper() in expected_mbti
    ]

    if len(mbti_columns) != 16:
        raise ValueError(
            f"MBTI 열 16개가 필요합니다. "
            f"현재 {len(mbti_columns)}개입니다."
        )

    df = df.rename(
        columns={
            col: col.strip().upper()
            for col in mbti_columns
        }
    )

    mbti_columns = sorted(expected_mbti)

    df["Country"] = (
        df["Country"]
        .astype("string")
        .str.strip()
    )

    df = df.dropna(subset=["Country"])
    df = df[df["Country"] != ""]

    for col in mbti_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    df[mbti_columns] = (
        df[mbti_columns].fillna(0)
    )

    df = df.drop_duplicates(
        subset=["Country"],
        keep="first"
    )

    if df.empty:
        raise ValueError("분석할 국가 데이터가 없습니다.")

    return df, mbti_columns


# 4. CSV 자동 불러오기
csv_path = find_csv_file()
file_bytes = None

if csv_path is not None:
    try:
        file_bytes = csv_path.read_bytes()
        st.success(
            f"✅ CSV 파일 불러오기 성공: {csv_path.name}"
        )

    except OSError as error:
        st.warning(f"파일 읽기 오류: {error}")


# 5. CSV 직접 업로드
if file_bytes is None:

    st.warning(
        "CSV 파일을 찾지 못했습니다. "
        "아래에서 직접 업로드해 주세요."
    )

    uploaded_file = st.file_uploader(
        "📂 CSV 파일 업로드",
        type=["csv"]
    )

    if uploaded_file is None:
        st.info(
            "GitHub에 CSV 파일을 올리거나 "
            "위에서 직접 업로드해 주세요."
        )
        st.stop()

    file_bytes = uploaded_file.getvalue()


# 6. 데이터 검증
try:
    df, mbti_columns = load_data(file_bytes)

except Exception as error:
    st.error(f"CSV 데이터 오류: {error}")
    st.stop()


# 7. 색상 함수
def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")

    return tuple(
        int(hex_color[i:i+2], 16)
        for i in (0, 2, 4)
    )


def rgb_to_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def interpolate_color(start, end, amount):

    start_rgb = hex_to_rgb(start)
    end_rgb = hex_to_rgb(end)

    rgb = tuple(
        round(
            start_rgb[i] +
            (end_rgb[i] - start_rgb[i]) * amount
        )
        for i in range(3)
    )

    return rgb_to_hex(rgb)


# 8. 순위별 색상 만들기
def make_rank_colors(count):

    if count <= 0:
        return []

    colors = ["#E53935"]

    if count == 1:
        return colors

    blue_start = "#1557A0"
    blue_end = "#DCEBFF"

    remaining = count - 1

    for i in range(remaining):

        amount = i / max(remaining - 1, 1)

        colors.append(
            interpolate_color(
                blue_start,
                blue_end,
                amount
            )
        )

    return colors


# 9. 분석 탭
tab1, tab2 = st.tabs([
    "🌍 국가별 MBTI 분석",
    "🏆 MBTI별 국가 순위"
])


# ================================================
# 탭 1. 국가를 선택하면 MBTI 16개 비율 표시
# ================================================
with tab1:

    st.subheader("🌍 국가별 MBTI 유형 분석")

    countries = sorted(
        df["Country"].astype(str).unique().tolist()
    )

    selected_country = st.selectbox(
        "분석할 국가를 선택하세요.",
        countries,
        key="country_selector"
    )

    country_data = df.loc[
        df["Country"] == selected_country,
        mbti_columns
    ].iloc[0]

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

    chart_data["Percentage"] = (
        chart_data["Ratio"] * 100
    )

    top_mbti = chart_data.iloc[0]["MBTI"]
    top_percentage = chart_data.iloc[0]["Percentage"]

    col1, col2, col3 = st.columns(3)

    col1.metric("🌎 분석 국가", selected_country)
    col2.metric("🥇 1위 MBTI", top_mbti)
    col3.metric(
        "📊 1위 비율",
        f"{top_percentage:.2f}%"
    )

    colors = make_rank_colors(len(chart_data))

    fig = go.Figure(
        go.Bar(
            x=chart_data["Percentage"],
            y=chart_data["MBTI"],
            orientation="h",
            marker=dict(color=colors),
            text=[
                f"{v:.2f}%"
                for v in chart_data["Percentage"]
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

    fig.update_layout(
        title=f"🇺🇳 {selected_country}의 MBTI 비율",
        xaxis_title="비율 (%)",
        yaxis_title="MBTI 유형",
        xaxis=dict(
            ticksuffix="%",
            rangemode="tozero",
            showgrid=True
        ),
        yaxis=dict(
            autorange="reversed"
        ),
        height=650,
        margin=dict(
            l=30,
            r=75,
            t=75,
            b=45
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.subheader("📋 국가별 MBTI 순위")

    country_table = chart_data.copy()

    country_table.insert(
        0,
        "순위",
        range(1, len(country_table) + 1)
    )

    country_table["비율"] = (
        country_table["Percentage"]
        .map(lambda v: f"{v:.2f}%")
    )

    st.dataframe(
        country_table[["순위", "MBTI", "비율"]],
        use_container_width=True,
        hide_index=True
    )


# ================================================
# 탭 2. MBTI를 선택하면 국가 순위 표시
# ================================================
with tab2:

    st.subheader("🏆 MBTI 유형별 국가 순위")

    selected_mbti = st.selectbox(
        "분석할 MBTI 유형을 선택하세요.",
        mbti_columns,
        key="mbti_selector"
    )

    ranking_data = df[
        ["Country", selected_mbti]
    ].copy()

    ranking_data[selected_mbti] = pd.to_numeric(
        ranking_data[selected_mbti],
        errors="coerce"
    ).fillna(0)

    # 비율이 높은 국가부터 정렬
    ranking_data = (
        ranking_data
        .sort_values(
            by=selected_mbti,
            ascending=False,
            kind="stable"
        )
        .reset_index(drop=True)
    )

    top_country = ranking_data.iloc[0]["Country"]

    top_percentage = (
        ranking_data.iloc[0][selected_mbti] * 100
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("🧠 선택 MBTI", selected_mbti)

    col2.metric("🥇 1위 국가", str(top_country))

    col3.metric(
        "📊 1위 비율",
        f"{top_percentage:.2f}%"
    )

    # 상위 20개 국가 그래프
    top_n = min(20, len(ranking_data))

    top_data = ranking_data.head(top_n).copy()

    top_data["Percentage"] = (
        top_data[selected_mbti] * 100
    )

    ranking_colors = make_rank_colors(
        len(top_data)
    )

    fig2 = go.Figure(
        go.Bar(
            x=top_data["Percentage"],
            y=top_data["Country"],
            orientation="h",
            marker=dict(color=ranking_colors),
            text=[
                f"{v:.2f}%"
                for v in top_data["Percentage"]
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

    fig2.update_layout(
        title=f"🌍 {selected_mbti} 비율 국가 TOP {top_n}",
        xaxis_title=f"{selected_mbti} 비율 (%)",
        yaxis_title="국가",
        xaxis=dict(
            ticksuffix="%",
            rangemode="tozero",
            showgrid=True
        ),
        yaxis=dict(
            autorange="reversed"
        ),
        height=max(550, top_n * 32),
        margin=dict(
            l=30,
            r=80,
            t=75,
            b=45
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )

    st.caption(
        f"그래프는 상위 {top_n}개 국가를 표시합니다. "
        f"아래 표에서는 전체 {len(ranking_data)}개 국가를 확인할 수 있습니다."
    )

    # 전체 국가 순위표
    st.subheader(
        f"🥇 {selected_mbti} 전체 국가 순위"
    )

    full_ranking = ranking_data.copy()

    full_ranking.insert(
        0,
        "순위",
        range(1, len(full_ranking) + 1)
    )

    full_ranking["비율"] = (
        full_ranking[selected_mbti] * 100
    ).map(lambda v: f"{v:.2f}%")

    st.dataframe(
        full_ranking[
            ["순위", "Country", "비율"]
        ].rename(
            columns={"Country": "국가"}
        ),
        use_container_width=True,
        hide_index=True
    )


# 10. 데이터 안내
with st.expander("ℹ️ 데이터 이용 안내"):

    st.write("""
    - 업로드된 CSV 파일을 바탕으로 분석합니다.
    - 원본 소수 데이터를 100배 하여 백분율로 표시합니다.
    - 조사 연도, 표본 크기 및 조사 방법은 CSV 파일에서 확인할 수 없습니다.
    - 결과는 참고용이며 국가 전체 국민의 성격을 단정하지 않습니다.
    """)


st.caption(
    "🌍 세계 국가별 MBTI 분석 | Streamlit Cloud"
)
