import streamlit as nn
import streamlit as st
import random

# 페이지 기본 설정
st.set_page_config(
    page_title="은하계 외계인 사랑 매칭",
    page_icon="👽",
    layout="centered"
)

# 타이틀 및 인트로
st.title("🛸 은하계 외계인 사랑 매칭")
st.subheader("당신과 운명의 주파수를 공유하는 외계인 짝꿍은 누구일까요?")
st.write("몇 가지 질문을 통해 당신의 성향을 분석하고, 완벽한 우주 파트너를 추천해 드립니다.")
st.markdown("---")

# 사용자 정보 입력
name = st.text_input("당신의 이름을 입력해 주세요:", placeholder="지구인 이름")

# 성향 분석 질문지
st.markdown("### 🪐 우주 성향 테스트")

q1 = st.radio(
    "1. 주말에 당신이 가고 싶은 곳은?",
    ["조용하고 평화로운 안드로메다 도서관", "시끌벅적하고 춤추는 화성의 클럽"]
)

q2 = st.radio(
    "2. 만약 당신에게 초능력이 생긴다면?",
    ["상대방의 마음을 읽는 텔레파시", "시공간을 마음대로 워프하는 능력"]
)

q3 = st.radio(
    "3. 연인과 데이트 중 우주선이 고장 났다면 당신의 반응은?",
    ["'걱정 마, 매뉴얼을 찾아보자!' 철저한 이성적 해결책 마련", "'이것도 우리 우주의 낭만이야!' 쏟아지는 별을 보며 감성에 젖음"]
)

q4 = st.radio(
    "4. 여행 계획을 세울 때 당신의 스타일은?",
    ["행성별 도착 시간과 루트를 분 단위로 짠다", "일단 블랙홀 근처로 가보고 끌리는 데로 들어간다"]
)

# 결과 확인 버튼
if st.button("💖 운명의 외계인 매칭하기"):
    if not name:
        st.warning("이름을 입력해 주셔야 은하계 데이터베이스에서 매칭이 시작됩니다!")
    else:
        st.balloons()
        
        # 성향 분석 로직을 간단한 MBTI 매핑으로 변환
        # E/I (외향/내향)
        ei = "I" if "안드로메다" in q1 else "E"
        # N/S (직관/감각 - 여기서는 텔레파시/워프로 대변)
        ns = "N" if "텔레파시" in q2 else "S"
        # T/F (사고/감정)
        tf = "T" if "매뉴얼" in q3 else "F"
        # J/P (판단/인식)
        jp = "J" if "분 단위" in q4 else "P"
        
        mbti_result = f"{ei}{ns}{tf}{jp}"
        
        # 외계인 캐릭터 데이터베이스
        alien_database = {
            "INTJ": {
                "name": "젤다르-9 (Zeldar-
