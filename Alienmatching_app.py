import streamlit as st
import math
import random

st.set_page_config(
    page_title="👽 Alien Love Match",
    page_icon="🛸",
    layout="centered"
)

st.title("👽 Alien Love Match")
st.subheader("당신과 가장 잘 맞는 외계인을 찾아드립니다 💕")

st.write("각 항목을 선택하면 당신의 성향을 분석하여 가장 잘 맞는 외계인을 추천합니다.")

# -------------------------------------------------
# 외계인 데이터
# -------------------------------------------------

aliens = [
    {
        "name": "조그(Zorg)",
        "emoji": "👾",
        "planet": "안드로메다 X-13",
        "description": "우주 바이크를 타고 은하계를 여행하는 자유로운 영혼.",
        "traits": {
            "activity": 95,
            "romance": 60,
            "humor": 80,
            "logic": 30,
            "adventure": 95,
        },
    },
    {
        "name": "루나(Luna-9)",
        "emoji": "🌙",
        "planet": "달의 뒷면",
        "description": "별을 바라보며 시를 쓰는 감성 외계인.",
        "traits": {
            "activity": 30,
            "romance": 95,
            "humor": 45,
            "logic": 55,
            "adventure": 25,
        },
    },
    {
        "name": "맥스론(Maxron)",
        "emoji": "🤖",
        "planet": "기계행성 MX",
        "description": "사랑도 알고리즘이라고 믿는 천재 AI.",
        "traits": {
            "activity": 55,
            "romance": 35,
            "humor": 50,
            "logic": 98,
            "adventure": 60,
        },
    },
    {
        "name": "블립(Blip)",
        "emoji": "🪼",
        "planet": "젤리성운",
        "description": "항상 웃고 노는 우주의 분위기 메이커.",
        "traits": {
            "activity": 80,
            "romance": 70,
            "humor": 98,
            "logic": 30,
            "adventure": 70,
        },
    },
    {
        "name": "네뷸라(Nebula)",
        "emoji": "✨",
        "planet": "오리온 성운",
        "description": "별빛을 연주하는 신비로운 음악가.",
        "traits": {
            "activity": 60,
            "romance": 92,
            "humor": 60,
            "logic": 65,
            "adventure": 55,
        },
    },
    {
        "name": "크로노(Chrono)",
        "emoji": "⏳",
        "planet": "시간 행성",
        "description": "시간을 여행하며 완벽한 데이트를 계획한다.",
        "traits": {
            "activity": 50,
            "romance": 80,
            "humor": 55,
            "logic": 88,
            "adventure": 40,
        },
    },
]

# -------------------------------------------------
# 설문
# -------------------------------------------------

name = st.text_input("이름")

activity = st.slider(
    "🏃 활동적인 것을 얼마나 좋아하나요?",
    0,
    100,
    50,
)

romance = st.slider(
    "💕 로맨틱한 분위기를 얼마나 좋아하나요?",
    0,
    100,
    50,
)

humor = st.slider(
    "😂 유머감각이 얼마나 중요하다고 생각하나요?",
    0,
    100,
    50,
)

logic = st.slider(
    "🧠 논리적인 사람을 얼마나 선호하나요?",
    0,
    100,
    50,
)

adventure = st.slider(
    "🚀 모험심은 어느 정도인가요?",
    0,
    100,
    50,
)

# -------------------------------------------------
# 궁합 계산
# -------------------------------------------------

def compatibility(user, alien):

    distance = math.sqrt(
        (user["activity"] - alien["activity"]) ** 2
        + (user["romance"] - alien["romance"]) ** 2
        + (user["humor"] - alien["humor"]) ** 2
        + (user["logic"] - alien["logic"]) ** 2
        + (user["adventure"] - alien["adventure"]) ** 2
    )

    max_distance = math.sqrt(5 * (100 ** 2))

    score = (1 - distance / max_distance) * 100

    score += random.uniform(-2, 2)

    return round(max(0, min(score, 100)), 1)


# -------------------------------------------------
# 결과
# -------------------------------------------------

if st.button("🛸 운명의 외계인 찾기"):

    user = {
        "activity": activity,
        "romance": romance,
        "humor": humor,
        "logic": logic,
        "adventure": adventure,
    }

    ranking = []

    for alien in aliens:

        score = compatibility(user, alien["traits"])

        ranking.append((score, alien))

    ranking.sort(reverse=True, key=lambda x: x[0])

    best_score, best = ranking[0]

    st.balloons()

    st.divider()

    st.header(f"{best['emoji']} {best['name']}")

    st.write(f"🌍 **출신 행성:** {best['planet']}")

    st.progress(best_score / 100)

    st.metric("❤️ 궁합", f"{best_score}%")

    st.write(best["description"])

    st.subheader("💘 왜 잘 맞을까요?")

    reasons = []

    for key, title in [
        ("activity", "활동성"),
        ("romance", "로맨틱 성향"),
        ("humor", "유머감각"),
        ("logic", "논리성"),
        ("adventure", "모험심"),
    ]:

        diff = abs(user[key] - best["traits"][key])

        if diff <= 10:
            reasons.append(f"✅ {title}이 거의 완벽하게 일치합니다.")

        elif diff <= 25:
            reasons.append(f"💚 {title}이 상당히 비슷합니다.")

    if len(reasons) == 0:
        reasons.append("✨ 서로 다른 성향이라 오히려 서로에게 끌릴 가능성이 큽니다.")

    for r in reasons:
        st.write(r)

    st.success(f"{name}님과 가장 잘 맞는 외계인은 **{best['name']}** 입니다!")

    st.divider()

    st.subheader("🏆 궁합 순위")

    for score, alien in ranking:

        st.write(
            f"{alien['emoji']} **{alien['name']}**  |  ❤️ {score}%"
        )
