
import streamlit as st
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울 관광지도 & 1박2일 여행",
    page_icon="🗺️",
    layout="wide"
)

# ==========================================
# 2. 화면 디자인
# ==========================================

st.markdown("""
<style>
.main {
    background-color: #f7f9fc;
}
h1 {
    color: #163b65;
    text-align: center;
}
.subtitle {
    text-align: center;
    color: #666666;
    font-size: 18px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 제목
# ==========================================

st.title("🗺️ 서울 인기 관광지 TOP 10")

st.markdown(
    '<p class="subtitle">'
    '외국인 관광객을 위한 서울 1박 2일 여행 가이드 🇰🇷'
    '</p>',
    unsafe_allow_html=True
)

st.write("")

st.info(
    "📍 서울의 대표 관광지 10곳을 지도에서 확인하고 "
    "1박 2일 추천 여행 코스를 만나보세요!"
)

# ==========================================
# 4. 관광지 데이터
# ==========================================

places = [
    {
        "no": 1,
        "name": "명동 거리",
        "english": "Myeongdong",
        "lat": 37.5636,
        "lon": 126.9869,
        "emoji": "🛍️",
        "description": "화장품, 패션 매장, 길거리 음식이 모여 있는 대표 쇼핑 거리입니다.",
        "english_desc": "A famous shopping district with cosmetics, fashion and street food."
    },
    {
        "no": 2,
        "name": "남산서울타워",
        "english": "N Seoul Tower",
        "lat": 37.5512,
        "lon": 126.9882,
        "emoji": "🗼",
        "description": "서울의 아름다운 전경을 360도로 감상할 수 있는 대표 랜드마크입니다.",
        "english_desc": "An iconic landmark with panoramic views of Seoul."
    },
    {
        "no": 3,
        "name": "경복궁",
        "english": "Gyeongbokgung Palace",
        "lat": 37.5796,
        "lon": 126.9770,
        "emoji": "🏯",
        "description": "조선 왕조의 대표 궁궐로 한국의 전통 건축과 역사를 만날 수 있습니다.",
        "english_desc": "The largest royal palace of the Joseon Dynasty."
    },
    {
        "no": 4,
        "name": "북촌한옥마을",
        "english": "Bukchon Hanok Village",
        "lat": 37.5826,
        "lon": 126.9830,
        "emoji": "🏘️",
        "description": "전통 한옥이 이어진 골목에서 한국의 옛 주거 문화를 느낄 수 있습니다.",
        "english_desc": "A traditional neighborhood with beautiful Korean houses."
    },
    {
        "no": 5,
        "name": "홍대 레드로드",
        "english": "Hongdae Red Road",
        "lat": 37.5563,
        "lon": 126.9236,
        "emoji": "🎸",
        "description": "버스킹, 음악, 개성 있는 상점과 카페로 유명한 젊음의 거리입니다.",
        "english_desc": "A lively area famous for music and street performances."
    },
    {
        "no": 6,
        "name": "광장시장",
        "english": "Gwangjang Market",
        "lat": 37.5700,
        "lon": 126.9998,
        "emoji": "🥢",
        "description": "빈대떡과 김밥 등 다양한 한국 음식을 맛볼 수 있는 전통시장입니다.",
        "english_desc": "A traditional market famous for Korean street food."
    },
    {
        "no": 7,
        "name": "동대문디자인플라자",
        "english": "Dongdaemun Design Plaza",
        "lat": 37.5671,
        "lon": 127.0095,
        "emoji": "🏙️",
        "description": "독특한 건축물과 전시, 디자인 행사를 즐길 수 있는 복합문화공간입니다.",
        "english_desc": "A modern landmark hosting design exhibitions and events."
    },
    {
        "no": 8,
        "name": "코엑스 별마당도서관",
        "english": "Starfield Library",
        "lat": 37.5117,
        "lon": 127.0592,
        "emoji": "📚",
        "description": "높은 책장과 개방적인 공간이 인상적인 인기 문화 명소입니다.",
        "english_desc": "A beautiful open library with towering bookshelves."
    },
    {
        "no": 9,
        "name": "성수동 카페거리",
        "english": "Seongsu Cafe Street",
        "lat": 37.5445,
        "lon": 127.0560,
        "emoji": "☕",
        "description": "개성 있는 카페와 편집숍이 모여 있는 트렌디한 거리입니다.",
        "english_desc": "A trendy neighborhood filled with unique cafes and shops."
    },
    {
        "no": 10,
        "name": "서울숲",
        "english": "Seoul Forest",
        "lat": 37.5444,
        "lon": 127.0374,
        "emoji": "🌳",
        "description": "도심 속에서 산책과 휴식을 즐길 수 있는 넓은 시민공원입니다.",
        "english_desc": "A spacious urban park ideal for walking and relaxing."
    }
]

# ==========================================
# 5. 서울 지도 생성
# ==========================================

seoul_map = folium.Map(
    location=[37.5665, 126.9780],
    zoom_start=11,
    tiles="OpenStreetMap"
)

# ==========================================
# 6. 지도에 관광지 마커 표시
# ==========================================

for place in places:

    popup_html = f"""
    <div style="width:220px;">
        <h3>{place['emoji']} {place['name']}</h3>
        <b>{place['english']}</b>
        <p>{place['description']}</p>
    </div>
    """

    folium.Marker(
        location=[
            place["lat"],
            place["lon"]
        ],

        tooltip=f"{place['no']}. {place['name']}",

        popup=folium.Popup(
            popup_html,
            max_width=280
        ),

        icon=folium.DivIcon(
            html=f"""
            <div style="
                background:#e63946;
                color:white;
                border:2px solid white;
                border-radius:50%;
                width:30px;
                height:30px;
                text-align:center;
                line-height:26px;
                font-weight:bold;
                box-shadow:0 1px 5px rgba(0,0,0,.4);
            ">
                {place['no']}
            </div>
            """,
            icon_size=(30, 30),
            icon_anchor=(15, 15)
        )

    ).add_to(seoul_map)

# ==========================================
# 7. 지도 출력
# ==========================================

st.subheader("📍 서울 관광지 위치 지도")

st_folium(
    seoul_map,
    width=None,
    height=560,
    use_container_width=True,
    returned_objects=[]
)

st.caption(
    "※ 지도는 OpenStreetMap을 사용합니다. "
    "인터넷 연결이 필요합니다."
)

# ==========================================
# 8. 1박 2일 여행 일정 데이터
# ==========================================

schedule = [
    {
        "날짜": "DAY 1",
        "시간": "09:00~10:45",
        "관광지": "🏯 경복궁",
        "일정": "궁궐 관람 및 한복 체험",
        "구분": "관광"
    },
    {
        "날짜": "DAY 1",
        "시간": "10:45~12:00",
        "관광지": "🏘️ 북촌한옥마을",
        "일정": "전통 한옥 골목 산책",
        "구분": "도보 이동 포함"
    },
    {
        "날짜": "DAY 1",
        "시간": "12:00~12:30",
        "관광지": "🚇 이동",
        "일정": "광장시장으로 이동",
        "구분": "약 30분"
    },
    {
        "날짜": "DAY 1",
        "시간": "12:30~14:00",
        "관광지": "🥢 광장시장",
        "일정": "빈대떡, 김밥 등 한국 음식 체험",
        "구분": "점심 및 관광"
    },
    {
        "날짜": "DAY 1",
        "시간": "14:00~14:20",
        "관광지": "🚇 이동",
        "일정": "DDP로 이동",
        "구분": "약 20분"
    },
    {
        "날짜": "DAY 1",
        "시간": "14:20~15:30",
        "관광지": "🏙️ DDP",
        "일정": "건축물 감상 및 전시 관람",
        "구분": "관광"
    },
    {
        "날짜": "DAY 1",
        "시간": "15:30~16:00",
        "관광지": "🚇 이동",
        "일정": "명동으로 이동",
        "구분": "약 30분"
    },
    {
        "날짜": "DAY 1",
        "시간": "16:00~17:30",
        "관광지": "🛍️ 명동",
        "일정": "쇼핑과 길거리 음식 체험",
        "구분": "관광"
    },
    {
        "날짜": "DAY 1",
        "시간": "17:30~18:10",
        "관광지": "🚇 이동",
        "일정": "남산서울타워로 이동",
        "구분": "약 40분"
    },
    {
        "날짜": "DAY 1",
        "시간": "18:10~20:00",
        "관광지": "🗼 남산서울타워",
        "일정": "서울 야경 감상 및 사진 촬영",
        "구분": "관광"
    },
    {
        "날짜": "DAY 2",
        "시간": "09:00~10:30",
        "관광지": "🌳 서울숲",
        "일정": "공원 산책 및 사진 촬영",
        "구분": "관광"
    },
    {
        "날짜": "DAY 2",
        "시간": "10:30~10:45",
        "관광지": "🚶 이동",
        "일정": "성수동으로 이동",
        "구분": "도보 약 15분"
    },
    {
        "날짜": "DAY 2",
        "시간": "10:45~12:30",
        "관광지": "☕ 성수동 카페거리",
        "일정": "카페, 팝업스토어, 쇼핑",
        "구분": "관광"
    },
    {
        "날짜": "DAY 2",
        "시간": "12:30~13:30",
        "관광지": "🍽️ 점심 식사",
        "일정": "성수동 맛집 탐방",
        "구분": "식사"
    },
    {
        "날짜": "DAY 2",
        "시간": "13:30~14:00",
        "관광지": "🚇 이동",
        "일정": "코엑스로 이동",
        "구분": "약 30분"
    },
    {
        "날짜": "DAY 2",
        "시간": "14:00~16:00",
        "관광지": "📚 별마당도서관",
        "일정": "독특한 책장과 실내 공간 감상",
        "구분": "관광"
    },
    {
        "날짜": "DAY 2",
        "시간": "16:00~17:00",
        "관광지": "🚇 이동",
        "일정": "홍대로 이동",
        "구분": "약 60분"
    },
    {
        "날짜": "DAY 2",
        "시간": "17:00~20:00",
        "관광지": "🎸 홍대 레드로드",
        "일정": "버스킹, 쇼핑, 거리 구경 및 저녁 식사",
        "구분": "관광"
    }
]

# ==========================================
# 9. 지도 아래 1박 2일 일정표
# ==========================================

st.divider()

st.header("🧳 서울 1박 2일 여행 추천 코스")

st.write(
    "오전 9시부터 오후 8시까지 "
    "서울의 대표 관광지 10곳을 둘러보는 일정입니다."
)

# DAY 1

st.subheader("🏯 DAY 1 | 전통문화와 서울 야경")

day1 = [
    row for row in schedule
    if row["날짜"] == "DAY 1"
]

st.table([
    {
        "시간": row["시간"],
        "장소": row["관광지"],
        "일정": row["일정"],
        "구분": row["구분"]
    }
    for row in day1
])

st.success(
    "DAY 1 TIP: 경복궁은 화요일 휴궁입니다. "
    "북촌한옥마을의 방문 제한 구역은 "
    "운영 시간과 방문 규칙을 확인하세요."
)

st.write("")

# DAY 2

st.subheader("☕ DAY 2 | 트렌디한 서울과 문화 체험")

day2 = [
    row for row in schedule
    if row["날짜"] == "DAY 2"
]

st.table([
    {
        "시간": row["시간"],
        "장소": row["관광지"],
        "일정": row["일정"],
        "구분": row["구분"]
    }
    for row in day2
])

st.success(
    "DAY 2 TIP: 성수동에서 카페를 즐기고 "
    "코엑스 별마당도서관을 둘러본 후 "
    "저녁에는 홍대의 활기찬 분위기를 즐겨보세요!"
)

st.caption(
    "※ 이동 시간은 예상 시간이며 교통 상황과 대기 시간에 따라 달라집니다."
)

# ==========================================
# 10. 관광지 설명
# ==========================================

st.divider()

st.header("✨ 서울 관광지 TOP 10 소개")

st.write(
    "각 관광지의 특징을 한국어와 영어로 확인해 보세요."
)

for i in range(0, len(places), 2):

    columns = st.columns(2)

    for column, place in zip(
        columns,
        places[i:i+2]
    ):

        with column:

            with st.container(border=True):

                st.subheader(
                    f"{place['emoji']} {place['no']}. {place['name']}"
                )

                st.markdown(
                    f"**{place['english']}**"
                )

                st.write(
                    place["description"]
                )

                st.caption(
                    place["english_desc"]
                )

                google_map_url = (
                    "https://www.google.com/maps/search/?api=1&query="
                    f"{place['lat']},{place['lon']}"
                )

                st.markdown(
                    f"[📌 Google 지도에서 위치 보기]({google_map_url})"
                )

# ==========================================
# 11. 여행 팁
# ==========================================

st.divider()

st.header("💡 서울 여행 TIP")

st.info("""
🏯 경복궁과 북촌한옥마을은 가까워 함께 방문하기 좋습니다.

🥢 광장시장에서는 다양한 한국 전통 음식을 맛보세요.

🗼 남산서울타워에서는 아름다운 서울 야경을 감상하세요.

☕ 성수동에서는 개성 있는 카페와 팝업스토어를 즐겨보세요.

🎸 홍대에서는 다양한 거리 공연과 쇼핑을 경험해 보세요.
""")

# ==========================================
# 12. 하단 안내
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:gray;">
        🇰🇷 SEOUL TRAVEL GUIDE<br>
        서울의 아름다운 관광지를 만나보세요!<br>
        Have a wonderful trip to Seoul!
    </div>
    """,
    unsafe_allow_html=True
)
