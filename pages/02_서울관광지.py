
import streamlit as st
import folium
from streamlit_folium import st_folium

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="서울 인기 관광지 TOP 10",
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
.place-card {
    background-color: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e5e7eb;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 제목
# ==========================================

st.title("🗺️ 서울 인기 관광지 TOP 10")

st.markdown(
    '<p class="subtitle">'
    '외국인 관광객이 좋아하는 서울의 대표 관광지를 만나보세요! 🇰🇷'
    '</p>',
    unsafe_allow_html=True
)

st.write("")

st.info(
    "📍 지도에 표시된 숫자를 클릭하면 "
    "관광지의 이름과 설명을 확인할 수 있습니다."
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
        "english": "Seongsu Café Street",
        "lat": 37.5445,
        "lon": 127.0560,
        "emoji": "☕",
        "description": "개성 있는 카페와 편집숍이 모여 있는 트렌디한 거리입니다.",
        "english_desc": "A trendy neighborhood filled with unique cafés and shops."
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
# 7. 지도 화면 출력
# ==========================================

st.subheader("📍 서울 관광지 위치")

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
# 8. 관광지 설명
# ==========================================

st.divider()

st.header("✨ 서울 관광지 TOP 10 소개")

st.write(
    "각 관광지의 특징을 한국어와 영어로 확인해 보세요."
)

# 두 개의 열로 관광지 표시

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
# 9. 여행 팁
# ==========================================

st.divider()

st.header("💡 서울 여행 TIP")

st.success("""
🏯 경복궁과 북촌한옥마을은 가까워 함께 방문하기 좋습니다.

🛍️ 명동과 남산서울타워도 하루 일정으로 추천합니다.

☕ 성수동에서는 개성 있는 카페와 다양한 팝업스토어를 즐겨보세요.
""")

# ==========================================
# 10. 하단 안내
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:gray;">
        🇰🇷 SEOUL TRAVEL GUIDE<br>
        서울의 아름다운 관광지를 만나보세요!
    </div>
    """,
    unsafe_allow_html=True
)
