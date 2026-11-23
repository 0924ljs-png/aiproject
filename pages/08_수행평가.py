
import streamlit as st
import pandas as pd
from pathlib import Path
import re

st.set_page_config(
    page_title="AI 맞춤 디저트 & 가게 추천",
    page_icon="🍰",
    layout="wide"
)

st.title("🍰 AI 맞춤 디저트 & 가게 추천")
st.write("취향 설문에 답하면 디저트를 추천하고, 업로드한 제과점 영업 데이터에서 해당 지역의 가게를 찾아드려요.")
st.caption("설문과 데이터 항목을 비교하는 AI 스타일 추천 알고리즘입니다.")

BASE_DIR = Path(__file__).resolve().parent
BAKERY_FILE = BASE_DIR / "식품_제과점영업.csv"
DESSERT_FILE = BASE_DIR / "desserts.csv"

# ----------------------------------------
# 1. 디저트 데이터
# ----------------------------------------
DEFAULT_DESSERTS = [
    ["딸기 생크림 케이크", "케이크", "부드러운 생크림과 상큼한 딸기", 7800, "상큼함", "부드러움"],
    ["초콜릿 케이크", "케이크", "진한 초콜릿 풍미", 7200, "달콤함", "촉촉함"],
    ["치즈 케이크", "케이크", "꾸덕하고 부드러운 치즈", 6500, "고소함", "꾸덕함"],
    ["레드벨벳 케이크", "케이크", "촉촉한 시트와 크림치즈", 7000, "달콤함", "촉촉함"],
    ["마카롱", "쿠키·구움과자", "달콤한 필링이 들어간 과자", 2800, "달콤함", "쫀득함"],
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

DESSERT_COLUMNS = [
    "디저트명", "카테고리", "설명",
    "예시가격(원)", "맛", "식감"
]


@st.cache_data
def load_desserts():
    if DESSERT_FILE.exists():
        try:
            data = pd.read_csv(
                DESSERT_FILE,
                encoding="utf-8-sig"
            )

            if "예시가격(원)" not in data.columns and "예시가격" in data.columns:
                data["예시가격(원)"] = data["예시가격"]

            for col in DESSERT_COLUMNS:
                if col not in data.columns:
                    data[col] = ""

            data["예시가격(원)"] = pd.to_numeric(
                data["예시가격(원)"],
                errors="coerce"
            )

            data = data.dropna(
                subset=["디저트명", "예시가격(원)"]
            )

            if not data.empty:
                return data[DESSERT_COLUMNS].copy()

        except Exception:
            pass

    return pd.DataFrame(
        DEFAULT_DESSERTS,
        columns=DESSERT_COLUMNS
    )


def infer_taste(row):
    txt = str(row["디저트명"]) + " " + str(row["설명"])

    if any(w in txt for w in ["레몬", "딸기", "블루베리", "망고"]):
        return "상큼함"

    if any(w in txt for w in ["커피", "티라미수"]):
        return "쌉싸름함"

    if any(w in txt for w in ["버터", "치즈", "아몬드", "스콘", "크루아상", "에그타르트", "휘낭시에"]):
        return "고소함"

    return "달콤함"


def infer_texture(row):
    txt = str(row["디저트명"]) + " " + str(row["설명"])

    if any(w in txt for w in ["쿠키", "크루아상", "타르트", "츄러스", "와플"]):
        return "바삭함"

    if any(w in txt for w in ["푸딩", "판나코타"]):
        return "탱글탱글함"

    if any(w in txt for w in ["브라우니", "치즈 케이크", "바스크"]):
        return "꾸덕함"

    if any(w in txt for w in ["아이스크림", "무스", "생크림", "티라미수"]):
        return "부드러움"

    if "팬케이크" in txt or "도넛" in txt:
        return "폭신함"

    if "빙수" in txt:
        return "시원함"

    if "마카롱" in txt:
        return "쫀득함"

    return "촉촉함"


desserts = load_desserts()

desserts["맛"] = desserts.apply(
    lambda r: str(r["맛"]).strip()
    if pd.notna(r["맛"]) and str(r["맛"]).strip()
    else infer_taste(r),
    axis=1
)

desserts["식감"] = desserts.apply(
    lambda r: str(r["식감"]).strip()
    if pd.notna(r["식감"]) and str(r["식감"]).strip()
    else infer_texture(r),
    axis=1
)

# ----------------------------------------
# 2. 제과점 영업 데이터 불러오기
# ----------------------------------------
@st.cache_data
def load_bakeries(file_bytes=None):

    if file_bytes is not None:
        import io
        source = io.BytesIO(file_bytes)

        for enc in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
            try:
                source.seek(0)

                return pd.read_csv(
                    source,
                    encoding=enc,
                    dtype=str,
                    low_memory=False
                )

            except UnicodeDecodeError:
                continue

        return pd.DataFrame()

    if not BAKERY_FILE.exists():
        return pd.DataFrame()

    for enc in ["cp949", "euc-kr", "utf-8-sig", "utf-8"]:
        try:
            return pd.read_csv(
                BAKERY_FILE,
                encoding=enc,
                dtype=str,
                low_memory=False
            )

        except UnicodeDecodeError:
            continue

        except Exception:
            break

    return pd.DataFrame()


# ----------------------------------------
# 3. 사이드바
# ----------------------------------------
with st.sidebar:

    st.header("📁 가게 데이터")

    uploaded_file = st.file_uploader(
        "식품_제과점영업.csv 업로드",
        type=["csv"]
    )


if uploaded_file is not None:
    bakeries = load_bakeries(uploaded_file.getvalue())
else:
    bakeries = load_bakeries()


# ----------------------------------------
# 4. 가게 데이터 정리
# ----------------------------------------
required_cols = [
    "사업장명",
    "업태구분명",
    "도로명주소",
    "전화번호",
    "홈페이지"
]

if not bakeries.empty:

    for col in required_cols:
        if col not in bakeries.columns:
            bakeries[col] = ""

    bakery_only = bakeries[
        bakeries["업태구분명"]
        .fillna("")
        .astype(str)
        .str.contains("제과점영업", na=False)
    ].copy()

    bakery_only["주소"] = (
        bakery_only["도로명주소"]
        .fillna("")
        .astype(str)
    )

    if "지번주소" in bakery_only.columns:

        missing_addr = bakery_only["주소"].str.strip().eq("")

        bakery_only.loc[missing_addr, "주소"] = (
            bakery_only.loc[missing_addr, "지번주소"]
            .fillna("")
            .astype(str)
        )

    bakery_only["지역1"] = (
        bakery_only["주소"]
        .str.extract(r"^([^\s]+)", expand=False)
    )

    bakery_only["지역2"] = (
        bakery_only["주소"]
        .str.extract(r"^[^\s]+\s+([^\s]+)", expand=False)
    )

    bakery_only["사업장명"] = (
        bakery_only["사업장명"]
        .fillna("")
        .astype(str)
    )

    bakery_only = bakery_only[
        bakery_only["사업장명"].str.strip() != ""
    ]

else:
    bakery_only = pd.DataFrame()


# ----------------------------------------
# 5. 디저트 취향 설문
# ----------------------------------------
st.header("1️⃣ 나의 디저트 취향 알아보기")

left, right = st.columns(2)

with left:

    taste = st.radio(
        "어떤 맛을 좋아하나요?",
        ["달콤함", "상큼함", "고소함", "쌉싸름함"],
        horizontal=True
    )

    texture = st.selectbox(
        "어떤 식감이 좋나요?",
        [
            "부드러움",
            "바삭함",
            "꾸덕함",
            "폭신함",
            "탱글탱글함",
            "촉촉함",
            "시원함",
            "쫀득함",
            "포슬포슬함"
        ]
    )

with right:

    dessert_category = st.selectbox(
        "어떤 종류가 먹고 싶나요?",
        ["종류 상관없음"] +
        sorted(
            desserts["카테고리"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )
    )

    budget = st.select_slider(
        "디저트 1개 예산",
        options=[3000, 5000, 7000, 10000, 15000],
        value=7000,
        format_func=lambda x: f"{x:,}원 이하"
    )


# ----------------------------------------
# 6. 가게 지역 선택
# ----------------------------------------
st.header("2️⃣ 가게를 찾을 지역 선택하기")

if not bakery_only.empty:

    provinces = sorted(
        bakery_only["지역1"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    provinces = [
        x for x in provinces
        if x and x != "nan"
    ]

    if provinces:

        province = st.selectbox(
            "시·도",
            provinces
        )

        districts = sorted(
            bakery_only.loc[
                bakery_only["지역1"] == province,
                "지역2"
            ]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        districts = [
            x for x in districts
            if x and x != "nan"
        ]

        district = st.selectbox(
            "시·군·구",
            ["전체"] + districts
        )

    else:
        province = ""
        district = "전체"

        st.warning("주소에서 지역 정보를 찾지 못했습니다.")

else:

    province = ""
    district = "전체"

    st.warning(
        "제과점 CSV 파일을 찾지 못했어요. "
        "왼쪽 메뉴에서 식품_제과점영업.csv 파일을 업로드해 주세요."
    )


search_word = st.text_input(
    "가게 이름 검색 (선택)",
    placeholder="예: 베이커리, 파리바게뜨, 빵집"
)


# ----------------------------------------
# 7. 추천 버튼
# ----------------------------------------
recommend = st.button(
    "✨ 내 취향 디저트와 가게 추천받기",
    type="primary",
    use_container_width=True
)


# ----------------------------------------
# 8. 추천 결과
# ----------------------------------------
if recommend:

    st.divider()

    st.header("🎉 맞춤 디저트 추천 결과")

    ranked = desserts.copy()

    ranked["추천점수"] = 0

    # 맛 일치
    ranked.loc[
        ranked["맛"] == taste,
        "추천점수"
    ] += 4

    # 식감 일치
    ranked.loc[
        ranked["식감"] == texture,
        "추천점수"
    ] += 4

    # 종류 일치
    if dessert_category != "종류 상관없음":

        ranked.loc[
            ranked["카테고리"] == dessert_category,
            "추천점수"
        ] += 5

    # 예산 일치
    ranked.loc[
        ranked["예시가격(원)"] <= budget,
        "추천점수"
    ] += 3

    ranked.loc[
        ranked["예시가격(원)"] > budget,
        "추천점수"
    ] -= 2

    ranked = ranked.sort_values(
        ["추천점수", "예시가격(원)"],
        ascending=[False, True]
    ).head(3)

    # TOP 3 표시
    cards = st.columns(3)

    medals = ["🥇 1위", "🥈 2위", "🥉 3위"]

    for idx, (_, item) in enumerate(ranked.iterrows()):

        with cards[idx]:

            st.subheader(medals[idx])

            st.markdown(
                f"### {item['디저트명']}"
            )

            st.write(
                f"**종류:** {item['카테고리']}"
            )

            st.write(
                f"**예시 가격:** {int(item['예시가격(원)']):,}원"
            )

            st.write(
                f"**맛 / 식감:** {item['맛']} · {item['식감']}"
            )

            st.write(item["설명"])

            st.caption(
                f"추천 점수: {int(item['추천점수'])}점"
            )

    st.caption(
        "디저트 가격은 예시 데이터이며 실제 판매 가격과 다를 수 있습니다."
    )

    # ------------------------------------
    # 9. 제과점 추천
    # ------------------------------------
    st.divider()

    st.header("📍 내 주변 제과점 추천")

    if bakery_only.empty:

        st.error(
            "가게 데이터가 없습니다. "
            "CSV 파일을 업로드한 뒤 다시 시도해 주세요."
        )

    else:

        shops = bakery_only.copy()

        # 지역 필터
        if province:

            shops = shops[
                shops["지역1"] == province
            ]

        if district != "전체":

            shops = shops[
                shops["지역2"] == district
            ]

        # 가게 이름 검색
        if search_word.strip():

            shops = shops[
                shops["사업장명"].str.contains(
                    search_word.strip(),
                    case=False,
                    na=False
                )
            ]

        # 디저트 종류별 가게 이름 키워드
        category_keywords = {

            "케이크": [
                "케이크", "케익", "cake"
            ],

            "쿠키·구움과자": [
                "쿠키", "마카롱", "베이크",
                "구움", "디저트"
            ],

            "아이스크림": [
                "아이스크림", "젤라또", "아이스"
            ],

            "푸딩·무스": [
                "푸딩", "무스", "디저트"
            ],

            "빵·페이스트리": [
                "베이커리", "브레드", "빵",
                "베이글", "제과"
            ],

            "와플·팬케이크": [
                "와플", "팬케이크", "디저트"
            ],

            "타르트": [
                "타르트", "파이", "디저트"
            ],

            "빙수": [
                "빙수", "설빙", "디저트"
            ]
        }

        # 가게 이름 키워드 점수로 정렬
        if dessert_category != "종류 상관없음":

            keys = category_keywords.get(
                dessert_category,
                []
            )

            if keys:

                shops["이름키워드점수"] = (
                    shops["사업장명"].apply(
                        lambda name: sum(
                            1 for key in keys
                            if key.lower() in str(name).lower()
                        )
                    )
                )

                shops = shops.sort_values(
                    "이름키워드점수",
                    ascending=False
                )

        if shops.empty:

            st.warning(
                "선택한 지역과 검색어에 맞는 제과점을 찾지 못했습니다. "
                "다른 지역이나 검색어를 선택해 보세요."
            )

        else:

            st.success(
                f"조건에 맞는 제과점 {len(shops):,}곳을 찾았습니다."
            )

            st.info(
                "중요: 업로드한 데이터에는 가게명·주소·전화번호 등의 "
                "정보가 있으며, 개별 매장의 실제 메뉴·가격·영업 중 여부·평점은 "
                "포함되어 있지 않습니다. 따라서 가게 목록은 지역과 가게명 "
                "키워드를 기준으로 정렬한 참고 정보입니다. "
                "방문 전 영업 여부와 메뉴를 확인하세요."
            )

            display = shops.head(30)

            for _, shop in display.iterrows():

                with st.container(border=True):

                    st.subheader(
                        str(shop.get("사업장명", "가게명 정보 없음"))
                    )

                    address = str(
                        shop.get("주소", "")
                    ).strip()

                    phone = str(
                        shop.get("전화번호", "")
                    ).strip()

                    homepage = str(
                        shop.get("홈페이지", "")
                    ).strip()

                    st.write(
                        f"📍 주소: {address if address and address != 'nan' else '주소 정보 없음'}"
                    )

                    st.write(
                        f"☎️ 전화번호: {phone if phone and phone != 'nan' else '등록된 전화번호 없음'}"
                    )

                    if homepage and homepage != "nan":

                        st.write(
                            f"🌐 홈페이지: {homepage}"
                        )

            if len(shops) > 30:

                st.caption(
                    "화면에는 상위 30개 가게만 표시했습니다. "
                    "지역이나 가게 이름으로 검색 범위를 좁혀 보세요."
                )

else:

    st.info(
        "설문과 지역을 선택한 뒤 추천 버튼을 눌러 주세요."
    )


st.divider()

st.caption(
    "🍰 AI 맞춤 디저트 & 제과점 추천 | 업로드한 제과점 영업 데이터 기반"
)
