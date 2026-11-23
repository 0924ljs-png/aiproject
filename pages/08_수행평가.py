
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="AI 디저트 추천",
    page_icon="🍰",
    layout="wide"
)

# --------------------------------
# 기본 디저트 데이터
# --------------------------------
DEFAULT_DATA = [
    ["딸기 생크림 케이크", "케이크", "부드러운 생크림과 상큼한 딸기", 7800, "상큼함", "부드러움"],
    ["초콜릿 케이크", "케이크", "진한 초콜릿 풍미", 7200, "달콤함", "촉촉함"],
    ["치즈 케이크", "케이크", "꾸덕하고 부드러운 치즈", 6500, "고소함", "꾸덕함"],
    ["레드벨벳 케이크", "케이크", "촉촉한 시트와 크림치즈", 7000, "달콤함", "촉촉함"],
    ["마카롱", "쿠키·구움과자", "달콤한 필링이 들어간 알록달록한 과자", 2800, "달콤함", "쫀득함"],
    ["초콜릿 쿠키", "쿠키·구움과자", "초콜릿 칩이 들어간 쿠키", 2500, "달콤함", "바삭함"],
    ["버터 쿠키", "쿠키·구움과자", "고소한 버터 향", 2200, "고소함", "바삭함"],
    ["브라우니", "쿠키·구움과자", "진하고 촉촉한 초콜릿", 3800, "달콤함", "꾸덕함"],
    ["휘낭시에", "쿠키·구움과자", "고소한 아몬드 구움과자", 2600, "고소함", "촉촉함"],
    ["스콘", "쿠키·구움과자", "담백하고 포슬포슬한 과자", 3500, "고소함", "포슬포슬함"],
    ["바닐라 아이스크림", "아이스크림", "부드러운 바닐라 맛", 4000, "달콤함", "부드러움"],
    ["초콜릿 아이스크림", "아이스크림", "진한 초콜릿 맛", 4500, "달콤함", "부드러움"],
    ["딸기 소프트아이스크림", "아이스크림", "상큼한 딸기 맛", 4800, "상큼함", "부드러움"],
    ["티라미수", "푸딩·무스", "커피와 마스카르포네 크림", 6500, "쌉싸름함", "부드러움"],
    ["판나코타", "푸딩·무스", "부드러운 이탈리아식 크림 디저트", 5500, "달콤함", "탱글탱글함"],
    ["초콜릿 무스", "푸딩·무스", "폭신한 초콜릿 디저트", 5800, "달콤함", "부드러움"],
    ["푸딩", "푸딩·무스", "탱글탱글한 달걀 푸딩", 4200, "달콤함", "탱글탱글함"],
    ["크루아상", "빵·페이스트리", "바삭한 버터 페이스트리", 3800, "고소함", "바삭함"],
    ["에그타르트", "빵·페이스트리", "부드러운 커스터드 타르트", 3200, "고소함", "바삭함"],
    ["시나몬 롤", "빵·페이스트리", "달콤한 시나몬 향", 4500, "달콤함", "촉촉함"],
    ["와플", "와플·팬케이크", "바삭하고 폭신한 와플", 5500, "달콤함", "바삭함"],
    ["팬케이크", "와플·팬케이크", "폭신한 팬케이크", 6000, "달콤함", "폭신함"],
    ["츄러스", "와플·팬케이크", "설탕과 시나몬을 묻힌 간식", 3500, "달콤함", "바삭함"],
    ["도넛", "빵·페이스트리", "달콤한 글레이즈 도넛", 3000, "달콤함", "폭신함"],
    ["레몬 타르트", "타르트", "상큼한 레몬 크림", 6200, "상큼함", "바삭함"],
    ["블루베리 타르트", "타르트", "블루베리와 부드러운 크림", 6800, "상큼함", "바삭함"],
    ["망고 빙수", "빙수", "망고와 곱게 간 얼음", 12000, "상큼함", "시원함"],
    ["팥빙수", "빙수", "팥과 떡을 올린 빙수", 10000, "달콤함", "시원함"],
    ["크렘 브륄레", "푸딩·무스", "달콤한 설탕층과 커스터드", 6500, "달콤함", "부드러움"],
    ["바스크 치즈 케이크", "케이크", "진하게 구운 치즈 케이크", 6800, "고소함", "꾸덕함"],
]

COLUMNS = [
    "디저트명", "카테고리", "설명",
    "예시가격(원)", "맛", "식감"
]


# --------------------------------
# CSV 파일 불러오기
# --------------------------------
@st.cache_data
def load_data():
    csv_path = Path(__file__).resolve().parent / "desserts.csv"

    if csv_path.exists():
        try:
            data = pd.read_csv(
                csv_path,
                encoding="utf-8-sig"
            )

            for col in COLUMNS:
                if col not in data.columns:
                    data[col] = ""

            if "예시가격(원)" not in data.columns and "예시가격" in data.columns:
                data["예시가격(원)"] = data["예시가격"]

            data["예시가격(원)"] = pd.to_numeric(
                data["예시가격(원)"],
                errors="coerce"
            )

            data = data.dropna(
                subset=["디저트명", "예시가격(원)"]
            )

            if not data.empty:
                return data[COLUMNS]

        except Exception:
            pass

    return pd.DataFrame(
        DEFAULT_DATA,
        columns=COLUMNS
    )


df = load_data()


# --------------------------------
# 맛과 식감 자동 분류
# --------------------------------
def infer_taste(row):
    text = str(row["디저트명"]) + " " + str(row["설명"])

    if any(x in text for x in ["레몬", "딸기", "블루베리", "망고"]):
        return "상큼함"

    if any(x in text for x in ["커피", "티라미수"]):
        return "쌉싸름함"

    if any(x in text for x in ["버터", "치즈", "아몬드", "스콘", "크루아상", "에그타르트", "휘낭시에"]):
        return "고소함"

    return "달콤함"


def infer_texture(row):
    text = str(row["디저트명"]) + " " + str(row["설명"])

    if any(x in text for x in ["쿠키", "크루아상", "타르트", "츄러스", "와플"]):
        return "바삭함"

    if any(x in text for x in ["푸딩", "판나코타"]):
        return "탱글탱글함"

    if any(x in text for x in ["브라우니", "치즈 케이크", "바스크"]):
        return "꾸덕함"

    if any(x in text for x in ["아이스크림", "무스", "생크림", "티라미수"]):
        return "부드러움"

    if "팬케이크" in text or "도넛" in text:
        return "폭신함"

    if "빙수" in text:
        return "시원함"

    if "마카롱" in text:
        return "쫀득함"

    return "촉촉함"


df["맛"] = df.apply(
    lambda r: r["맛"] if str(r["맛"]).strip() else infer_taste(r),
    axis=1
)

df["식감"] = df.apply(
    lambda r: r["식감"] if str(r["식감"]).strip() else infer_texture(r),
    axis=1
)


# --------------------------------
# 웹페이지 화면
# --------------------------------
st.title("🍰 나에게 딱 맞는 디저트 찾기")

st.write(
    "간단한 설문에 답하면 취향에 어울리는 "
    "디저트 TOP 3를 추천해 줄게요!"
)

st.caption(
    "설문 답변과 디저트 정보를 비교하는 "
    "AI 스타일 추천 알고리즘입니다."
)


# --------------------------------
# 설문 조사
# --------------------------------
with st.sidebar:

    st.header("🍓 디저트 취향 설문")

    taste = st.radio(
        "1. 어떤 맛을 좋아하나요?",
        ["달콤함", "상큼함", "고소함", "쌉싸름함"]
    )

    texture = st.radio(
        "2. 어떤 식감이 끌리나요?",
        [
            "부드러움",
            "바삭함",
            "꾸덕함",
            "폭신함",
            "탱글탱글함",
            "촉촉함",
            "시원함",
            "쫀득함"
        ]
    )

    categories = sorted(
        df["카테고리"].dropna().astype(str).unique().tolist()
    )

    category = st.selectbox(
        "3. 어떤 종류의 디저트를 원하나요?",
        ["모두 좋아요"] + categories
    )

    budget = st.select_slider(
        "4. 디저트 하나에 얼마까지 쓸 수 있나요?",
        options=[3000, 5000, 7000, 10000, 15000],
        value=7000,
        format_func=lambda x: f"{x:,}원 이하"
    )

    submitted = st.button(
        "✨ 내 취향 디저트 찾기",
        type="primary",
        use_container_width=True
    )


# --------------------------------
# 설문 결과 미리보기
# --------------------------------
st.subheader("🎯 나의 취향")

c1, c2, c3 = st.columns(3)

c1.metric("좋아하는 맛", taste)
c2.metric("선호 식감", texture)
c3.metric("예산", f"{budget:,}원 이하")


# --------------------------------
# 디저트 추천 알고리즘
# --------------------------------
if submitted:

    results = df.copy()

    results["점수"] = 0

    # 맛이 일치하면 4점
    results.loc[
        results["맛"] == taste,
        "점수"
    ] += 4

    # 식감이 일치하면 4점
    results.loc[
        results["식감"] == texture,
        "점수"
    ] += 4

    # 카테고리가 일치하면 5점
    if category != "모두 좋아요":

        results.loc[
            results["카테고리"] == category,
            "점수"
        ] += 5

    # 예산에 맞으면 3점
    results.loc[
        results["예시가격(원)"] <= budget,
        "점수"
    ] += 3

    # 예산을 초과하면 -2점
    results.loc[
        results["예시가격(원)"] > budget,
        "점수"
    ] -= 2

    # 높은 점수 순서로 정렬
    results = results.sort_values(
        by=["점수", "예시가격(원)"],
        ascending=[False, True]
    ).head(3)

    st.success(
        "설문 분석 완료! 당신의 취향에 어울리는 "
        "디저트를 찾았어요 🎉"
    )

    st.subheader("🏆 당신을 위한 디저트 TOP 3")

    cols = st.columns(3)

    medals = ["🥇 1위", "🥈 2위", "🥉 3위"]

    for i, (_, item) in enumerate(results.iterrows()):

        with cols[i]:

            st.markdown(f"### {medals[i]}")

            st.markdown(
                f"## {item['디저트명']}"
            )

            st.write(
                f"**종류:** {item['카테고리']}"
            )

            st.write(
                f"**가격:** {int(item['예시가격(원)']):,}원"
            )

            st.write(
                f"**맛:** {item['맛']}"
            )

            st.write(
                f"**식감:** {item['식감']}"
            )

            st.write(item["설명"])

            st.caption(
                f"취향 일치 점수: {int(item['점수'])}점"
            )

    st.info(
        "추천 결과는 설문과 등록된 데이터에 따른 참고용입니다. "
        "가격은 예시 가격이며 실제 판매 가격과 다를 수 있어요."
    )


else:

    st.info(
        "왼쪽 설문에 답한 다음 "
        "**내 취향 디저트 찾기** 버튼을 눌러 보세요!"
    )

    st.subheader("🍪 어떤 디저트가 있을까요?")

    preview = df[
        ["디저트명", "카테고리", "예시가격(원)"]
    ].copy()

    preview["예시가격(원)"] = preview[
        "예시가격(원)"
    ].apply(
        lambda x: f"{int(x):,}원"
    )

    st.dataframe(
        preview,
        use_container_width=True,
        hide_index=True
    )


st.divider()

st.caption(
    "🍰 디저트 추천 웹앱 | Streamlit Cloud에서 실행 가능"
)

