from datetime import datetime, timedelta
import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

# PAGE CONFIG
st.set_page_config(
    page_title="🎉 전국 축제 탐험대",
    page_icon="🎈",
    layout="wide",
)

# API CONFIG
# Streamlit Secrets 또는 GitHub Secrets에서 가져옴
API_KEY = st.secrets.get("TOUR_API_KEY", "")
BASE_URL = "http://apis.data.go.kr/B551011/KorService1"

AREA_CODES = {
    "전국": "",
    "서울": "1",
    "인천": "2",
    "대전": "3",
    "대구": "4",
    "광주": "5",
    "부산": "6",
    "울산": "7",
    "세종": "8",
    "경기": "31",
    "강원": "32",
    "충북": "33",
    "충남": "34",
    "전북": "35",
    "전남": "36",
    "경북": "37",
    "경남": "38",
    "제주": "39",
}

@st.cache_data(ttl=3600)
def fetch_festivals(event_start_date, area_code=""):
    """행사정보조회 API 호출"""
    url = f"{BASE_URL}/searchFestival1"
    params = {
        "serviceKey": API_KEY,
        "numOfRows": "50",
        "pageNo": "1",
        "MobileOS": "ETC",
        "MobileApp": "FestivalApp",
        "_type": "json",
        "listYN": "Y",
        "arrange": "A",
        "eventStartDate": event_start_date,
        "areaCode": area_code,
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        
        # 응답이 JSON이 아닐 경우(에러 페이지 등)를 대비해 텍스트 확인
        try:
            data = res.json()
        except Exception:
            st.error(f"API 서버가 JSON이 아닌 응답을 보냈어 (상태 코드: {res.status_code})")
            st.code(res.text[:500]) # 서버가 보낸 응답 앞부분 출력
            return []

        items = (
            data.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
        )
        if isinstance(items, dict):
            items = [items]
        return items
    except Exception as e:
        st.error(f"네트워크 오류 발생: {e}")
        return []
        
@st.cache_data(ttl=3600)
def fetch_nearby_places(map_x, map_y, radius=5000):
    """위치기반 관광정보 API 호출 (주변 5km 내 맛집/관광지)"""
    url = f"{BASE_URL}/locationBasedList1"
    params = {
        "serviceKey": API_KEY,
        "numOfRows": "10",
        "pageNo": "1",
        "MobileOS": "ETC",
        "MobileApp": "FestivalApp",
        "_type": "json",
        "mapX": map_x,
        "mapY": map_y,
        "radius": str(radius),
        "arrange": "E",  # 거리순
    }
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        items = (
            data.get("response", {})
            .get("body", {})
            .get("items", {})
            .get("item", [])
        )
        if isinstance(items, dict):
            items = [items]
        return items
    except Exception:
        return []


# UI & APP LOGIC
st.title("🎉 떠나자! 전국 축제 지도 탐험대")
st.caption(
    "한국관광공사 TourAPI를 활용하여 실시간 전국 축제 정보를 제공합니다."
)

if not API_KEY:
    st.warning(
        "⚠️ `TOUR_API_KEY`가 설정되지 않았습니다. `.streamlit/secrets.toml` 혹은 Streamlit Cloud Secrets에 API 키를 등록해주세요."
    )
    st.stop()

# SIDEBAR FILTERS
st.sidebar.header("🔍 축제 검색 필터")
selected_area = st.sidebar.selectbox("지역 선택", list(AREA_CODES.keys()))

today = datetime.today()
start_date = st.sidebar.date_input("시작일", today)
start_str = start_date.strftime("%Y%m%d")

# FETCH DATA
raw_data = fetch_festivals(start_str, AREA_CODES[selected_area])

if not raw_data:
    st.info("💡 해당 조건의 축제 정보가 없습니다.")
    st.stop()

df = pd.DataFrame(raw_data)

# TABS
tab1, tab2, tab3 = st.tabs(
    ["🗓️ 축제 목록", "🎲 랜덤 축제 뽑기", "🗺️ 축제 위치 지도"]
)

# TAB 1: FESTIVAL LIST & DETAIL
with tab1:
    st.subheader(f"총 {len(df)}개의 축제가 검색되었습니다.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.write("### 축제 리스트")
        selected_title = st.selectbox("상세 정보를 볼 축제를 선택하세요:", df["title"])
        selected_item = df[df["title"] == selected_title].iloc[0]

    with col2:
        st.markdown(f"## {selected_item['title']}")

        # 이미지 출력
        img_url = selected_item.get(
            "firstimage", "https://via.placeholder.com/400x250?text=No+Image"
        )
        st.image(img_url, use_container_width=True)

        st.markdown(
            f"**📅 기간:** {selected_item.get('eventstartdate')} ~ {selected_item.get('eventenddate')}"
        )
        st.markdown(f"**📍 주소:** {selected_item.get('addr1', '주소 정보 없음')}")

        # 카카오맵 길찾기 URL 생성
        if selected_item.get("mapx") and selected_item.get("mapy"):
            kakao_url = f"https://map.kakao.com/link/to/{selected_item['title']},{selected_item['mapy']},{selected_item['mapx']}"
            st.link_button("🚗 카카오맵으로 길찾기", kakao_url)

    st.divider()

    # 주변 맛집 및 관광지 파트
    st.subheader(f"📍 '{selected_item['title']}' 주변 즐길거리 (5km 이내)")
    if selected_item.get("mapx") and selected_item.get("mapy"):
        nearby_data = fetch_nearby_places(
            selected_item["mapx"], selected_item["mapy"]
        )
        if nearby_data:
            n_cols = st.columns(3)
            for idx, place in enumerate(nearby_data[:6]):
                with n_cols[idx % 3]:
                    st.write(f"**{place.get('title')}**")
                    p_img = place.get(
                        "firstimage",
                        "https://via.placeholder.com/200x120?text=No+Image",
                    )
                    st.image(p_img, use_container_width=True)
                    st.caption(f"주소: {place.get('addr1', '정보 없음')}")
        else:
            st.write("주변 정보가 없습니다.")


# TAB 2: RANDOM PICK (FUN FEATURE)
with tab2:
    st.subheader("🎲 이번 주말, 어디로 떠날지 모르겠다면?")
    st.write("버튼을 누르면 현재 조건 내의 축제 중 하나를 추천해 드립니다!")

    if st.button("✨ 축제 무료 뽑기!", type="primary"):
        st.balloons()
        random_item = df.sample(n=1).iloc[0]

        st.success(f"🎉 오늘의 추천 축제: **{random_item['title']}**")

        r_col1, r_col2 = st.columns([1, 1])
        with r_col1:
            r_img = random_item.get(
                "firstimage",
                "https://via.placeholder.com/400x250?text=No+Image",
            )
            st.image(r_img, use_container_width=True)
        with r_col2:
            st.write(f"**기간:** {random_item.get('eventstartdate')}부터")
            st.write(f"**주소:** {random_item.get('addr1', '정보 없음')}")


# TAB 3: MAP VIEW
with tab3:
    st.subheader("🗺️ 한눈에 보는 축제 지도")

    # 위도/경도가 있는 데이터만 필터링
    valid_map_df = df.dropna(subset=["mapx", "mapy"]).copy()
    valid_map_df["mapx"] = pd.to_numeric(valid_map_df["mapx"], errors="coerce")
    valid_map_df["mapy"] = pd.to_numeric(valid_map_df["mapy"], errors="coerce")
    valid_map_df = valid_map_df.dropna(subset=["mapx", "mapy"])

    if not valid_map_df.empty:
        # 중심점 계산
        avg_lat = valid_map_df["mapy"].mean()
        avg_lng = valid_map_df["mapx"].mean()

        m = folium.Map(location=[avg_lat, avg_lng], zoom_start=7)

        for _, row in valid_map_df.iterrows():
            folium.Marker(
                location=[row["mapy"], row["mapx"]],
                popup=row["title"],
                tooltip=row["title"],
                icon=folium.Icon(color="red", icon="star"),
            ).add_to(m)

        st_folium(m, width=900, height=500)
    else:
        st.write("지도에 표시할 좌표 데이터가 없습니다.")
