import random
from datetime import datetime
import pandas as pd
import requests
import streamlit as st

# --- 페이지 설정 ---
st.set_page_config(
    page_title="대한민국 구석구석: 오늘의 랜덤 축제",
    page_icon="🎉",
    layout="wide",
)

# --- 사이드바: API 설정 ---
st.sidebar.header("⚙️ API 설정")
default_key = (
    st.secrets.get("TOUR_API_KEY", "") if "TOUR_API_KEY" in st.secrets else ""
)
API_KEY = st.sidebar.text_input(
    "Tour API 인증키 (Decoding)", value=default_key, type="password"
)

# 한국관광공사 국문 관광정보 서비스 API 엔드포인트 (KorService1)
BASE_URL = "https://apis.data.go.kr/B551011/KorService1/searchFestival1"


# --- API 호출 함수 ---
@st.cache_data(ttl=3600)
def get_festivals(api_key, start_date):
  """한국관광공사 API를 통해 특정 일자 전후의 행사/축제 정보를 가져옵니다."""
  params = {
      "serviceKey": api_key,
      "MobileOS": "ETC",
      "MobileApp": "StreamlitFestivalApp",
      "_type": "json",
      "eventStartDate": start_date,
      "numOfRows": 100,
      "pageNo": 1,
  }

  try:
    response = requests.get(BASE_URL, params=params, timeout=10)

    # 500 에러 등 HTTP 에러 발생 시 처리
    if response.status_code != 200:
      st.error(
          f"🚨 한국관광공사 API 서버 오류 발생 (상태 코드:"
          f" {response.status_code}). 서버 점검 중이거나 일시적인 문제일"
          " 수 있습니다."
      )
      return []

    data = response.json()
    body = data.get("response", {}).get("body", {})
    items = body.get("items", {})

    if not items or items == "":
      return []

    return items.get("item", [])

  except requests.exceptions.RequestException as e:
    st.error(f"네트워크 연결 오류가 발생했습니다: {e}")
    return []
  except Exception as e:
    st.error(f"데이터를 처리하는 중 오류가 발생했습니다: {e}")
    return []


# --- 메인 화면 디자인 ---
st.title("🎉 오늘의 랜덤 축제 추천")
st.markdown(
    "한국관광공사 공공 API를 활용하여 지금 떠날 수 있는 전국의 다양한 축제 정보를"
    " 소개해드립니다."
)

if not API_KEY:
  st.warning(
      "⚠️ 사이드바에 한국관광공사 API 인증키(Decoding Key)를 입력해주세요!"
  )
else:
  today_str = datetime.today().strftime("%Y%m%d")

  with st.spinner("전국 축제 정보를 불러오는 중입니다..."):
    festival_list = get_festivals(API_KEY, today_str)

  if not festival_list:
    st.info(
        "💡 현재 공공데이터포털 API 서버 측의 500 에러로 인해 데이터를 가져오지"
        " 못했습니다.\n\n"
        "**해결 방법:**\n1. 잠시 후 새로고침을 시도해 보세요.\n2. 공공데이터포털"
        " 마이페이지에서 해당 API가 정상 승인 상태인지, 트래픽 한도가 초과되지"
        " 않았는지 확인해 주세요."
    )
  else:
    df = pd.DataFrame(festival_list)

    if "random_festival" not in st.session_state or st.button(
        "🎲 다른 랜덤 축제 뽑기"
    ):
      st.session_state["random_festival"] = random.choice(festival_list)

    current_pick = st.session_state["random_festival"]

    st.markdown("---")
    st.subheader("✨ 오늘의 스포트라이트 축제")

    col1, col2 = st.columns([1, 2])

    with col1:
      first_image = current_pick.get("firstimage", "")
      if first_image:
        st.image(first_image, use_container_width=True)
      else:
        st.info("등록된 대표 이미지가 없습니다.")

    with col2:
      st.markdown(f"### **{current_pick.get('title')}**")
      st.write(
          f"📅 **일정:** {current_pick.get('eventstartdate')} ~"
          f" {current_pick.get('eventenddate')}"
      )
      st.write(f"📍 **장소:** {current_pick.get('addr1', '상세 주소 없음')}")
      tel = current_pick.get("tel", "문의처 정보 없음")
      st.write(f"📞 **문의처:** {tel}")

    st.markdown("---")
    st.subheader("🔍 전체 축제 검색 및 리스트")

    search_keyword = st.text_input(
        "축제 이름 검색", placeholder="예: 바다, 불꽃, 서울 등"
    )

    if search_keyword:
      filtered_df = df[
          df["title"].str.contains(search_keyword, case=False, na=False)
      ]
    else:
      filtered_df = df

    st.write(f"총 **{len(filtered_df)}개**의 축제가 검색되었습니다.")

    if not filtered_df.empty:
      display_df = filtered_df[
          ["title", "eventstartdate", "eventenddate", "addr1"]
      ].copy()
      display_df.columns = ["축제명", "시작일", "종료일", "주소"]
      st.dataframe(display_df, use_container_width=True)
    else:
      st.warning("검색 결과가 없습니다.")
