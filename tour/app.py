import random
from datetime import datetime
import io
import pandas as pd
import requests
import streamlit as st

# 파이썬 버전에 따른 TOML 라이브러리 임포트 처리
try:
  import tomllib  # Python 3.11+
except ImportError:
  try:
    import tomli as tomllib  # Fallback for older python
  except ImportError:
    try:
      import toml as tomllib  # Fallback
    except ImportError:
      tomllib = None

# --- 페이지 설정 ---
st.set_page_config(
    page_title="대한민국 구석구석: 오늘의 랜덤 축제",
    page_icon="🎉",
    layout="wide",
)

# --- GitHub Secrets.toml에서 API Key 불러오기 ---
GITHUB_SECRETS_RAW_URL = "https://raw.githubusercontent.com/monet107/streamlit_App/main/tour/.streamlit/secrets.toml"


@st.cache_data(ttl=3600)
def load_api_key_from_github(url):
  """GitHub에 저장된 secrets.toml 파일을 원본(raw)으로 불러와 파싱합니다."""
  try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
      if tomllib:
        # TOML 파싱
        if hasattr(tomllib, "loads"):
          secrets_data = tomllib.loads(response.text)
        else:
          secrets_data = tomllib.load(io.BytesIO(response.content))
        return secrets_data.get("TOUR_API_KEY", "")
      else:
        # 라이브러리가 없을 경우 간단한 텍스트 파싱
        for line in response.text.splitlines():
          if "TOUR_API_KEY" in line:
            return line.split("=")[1].strip().strip('"').strip("'")
    return ""
  except Exception:
    return ""


# GitHub에서 인증키 자동 로드 시도
github_default_key = load_api_key_from_github(GITHUB_SECRETS_RAW_URL)

# --- 사이드바: API 설정 ---
st.sidebar.header("⚙️ API 설정")
# 스트림릿 시크릿에 있거나 GitHub에서 불러온 키를 기본값으로 지정
stored_key = (
    st.secrets.get("TOUR_API_KEY", "")
    if "TOUR_API_KEY" in st.secrets
    else github_default_key
)
API_KEY = st.sidebar.text_input(
    "Tour API 인증키 (Decoding)", value=stored_key, type="password"
)

# 한국관광공사 국문 관광정보 서비스 API 엔드포인트 (KorService1)
BASE_URL = "https://apis.data.go.kr/B551011/KorService1/searchFestival1"

# --- 임시 샘플 데이터 (API 서버 장애 시 앱 테스트용) ---
SAMPLE_FESTIVALS = [
    {
        "title": "[샘플] 서울 불꽃 페스티벌",
        "eventstartdate": "20261005",
        "eventenddate": "20261005",
        "addr1": "서울특별시 영등포구 여의동로 330",
        "tel": "02-120",
        "firstimage": "",
    },
    {
        "title": "[샘플] 보령 머드 축제",
        "eventstartdate": "20260718",
        "eventenddate": "20260810",
        "addr1": "충청남도 보령시 신흑동 123",
        "tel": "041-930-0891",
        "firstimage": "",
    },
    {
        "title": "[샘플] 부산 바다 축제",
        "eventstartdate": "20260801",
        "eventenddate": "20260806",
        "addr1": "부산광역시 해운대구 해운대해변로 264",
        "tel": "051-501-6051",
        "firstimage": "",
    },
]


# --- API 호출 함수 ---
@st.cache_data(ttl=3600)
def get_festivals(api_key, start_date):
  """한국관광공사 API를 호출하며, 타임아웃이나 오류 발생 시 샘플 데이터를 반환합니다."""
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
    response = requests.get(BASE_URL, params=params, timeout=15)

    if response.status_code != 200:
      st.warning(
          f"⚠️ API 서버 응답 코드({response.status_code}). 임시 샘플 데이터를"
          " 로드합니다."
      )
      return SAMPLE_FESTIVALS

    data = response.json()
    body = data.get("response", {}).get("body", {})
    items = body.get("items", {})

    if not items or items == "":
      st.info(
          "ℹ️ 조회된 데이터가 없어 임시 샘플 데이터를 대신 표시합니다."
      )
      return SAMPLE_FESTIVALS

    return items.get("item", [])

  except requests.exceptions.Timeout:
    st.warning(
        "⏱️ API 서버 응답 시간이 초과되었습니다 (Read timed out)."
        " 공공데이터포털 서버 상태가 불안정하여 임시 샘플 데이터를 표시합니다."
    )
    return SAMPLE_FESTIVALS
  except Exception as e:
    st.warning(
        f"⚠️ 오류가 발생하여 임시 샘플 데이터를 로드합니다. (사유: {e})"
    )
    return SAMPLE_FESTIVALS


# --- 메인 화면 디자인 ---
st.title("🎉 오늘의 랜덤 축제 추천")
st.markdown(
    "한국관광공사 공공 API를 활용하여 지금 떠날 수 있는 전국의 다양한 축제 정보를"
    " 소개해드립니다."
)

if not API_KEY:
  st.warning(
      "⚠️ API 인증키가 감지되지 않았습니다. 사이드바에 키를 직접 입력해"
      " 주세요."
  )
else:
  today_str = datetime.today().strftime("%Y%m%d")

  with st.spinner("전국 축제 정보를 불러오는 중입니다..."):
    festival_list = get_festivals(API_KEY, today_str)

  if not festival_list:
    festival_list = SAMPLE_FESTIVALS

  df = pd.DataFrame(festival_list)

  if "random_festival" not in st.session_state or st.button(
      "🎲 다른 랜덤 축제 뽑기"
  ):
    st.session_state["random_festival"] = random.choice(festival_list)

  current_pick = st.session_state["random_festival"]

  # --- [섹션 1] 오늘의 추천 랜덤 축제 카드 ---
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

  # --- [섹션 2] 전체 축제 목록 및 검색 필터 ---
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
