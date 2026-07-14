import streamlit as st
import random

st.set_page_config(
    page_title="👽 Alien Love Match",
    page_icon="🛸",
    layout="centered"
)

st.title("👽 외계인 사랑 매칭")
st.subheader("당신과 가장 잘 맞는 외계인을 찾아드립니다 ❤️")

# -------------------------
# 외계인 데이터
# -------------------------

aliens = [
    {
        "name": "조그(Zorg)",
        "planet": "안드로메다 X-13",
        "emoji": "👾",
        "likes": {
            "personality": "외향적",
            "hobby": "여행",
            "date": "모험",
            "adventure": "매우 높음"
        },
        "description": "우주 오토바이를 타고 은하계를 여행하는 낭만파."
    },
    {
        "name": "루나(Luna-9)",
        "planet": "달의 뒷면",
        "emoji": "🌙",
        "likes": {
            "personality": "차분함",
            "hobby": "독서",
            "date": "카페",
            "adventure": "낮음"
        },
        "description": "별빛 아래에서 책 읽는 것을 좋아하는 감성 외계인."
    },
    {
        "name": "블립(Blip)",
        "planet": "젤리성운",
        "emoji": "🪼",
        "likes": {
            "personality": "유쾌함",
            "hobby": "게임",
            "date": "놀이공원",
            "adventure": "보통"
        },
        "description": "항상 웃으며 젤리비를 뿌리고 다닌다."
    },
    {
        "name": "네뷸라(Nebula)",
        "planet": "오리온",
        "emoji": "✨",
        "likes": {
            "personality": "감성적",
            "hobby": "음악",
            "date": "산책",
            "adventure": "보통"
        },
        "description": "별의 노래를 연주하는 우주의 싱어송라이터."
    },
    {
        "name": "맥스론(Maxron)",
        "planet": "기계행성 MX",
        "emoji": "🤖",
        "likes": {
            "personality": "논리적",
            "hobby": "코딩",
            "date": "영화",
            "adventure": "높음"
        },
        "description": "사랑도 알고리즘이라고 믿는 AI 외계인."
    }
]

# -------------------------
# 입력
# -------------------------

name = st.text_input("이름")

personality = st.selectbox(
    "성격",
    ["외향적", "차분함", "유쾌함", "감성적", "논리적"]
)

hobby = st.selectbox(
    "취미",
    ["여행", "독서", "게임", "음악", "코딩"]
)

date = st.selectbox(
    "데이트 스타일",
    ["카페", "산책", "영화", "놀이공원", "모험"]
)

adventure = st.select_slider(
    "모험심",
    options=["낮음", "보통", "높음", "매우 높음"]
)

# -------------------------
# 매칭 함수
# -------------------------

def score(alien):
    s = 0

    if personality == alien["likes"]["personality"]:
        s += 30

    if hobby == alien["likes"]["hobby"]:
        s += 25

    if date == alien["likes"]["date"]:
        s += 25

    if adventure == alien["likes"]["adventure"]:
        s += 20

    s += random.randint(0, 10)

    return min(s, 100)


# -------------------------
# 결과
# -------------------------

if st.button("🛸 내 운명의 외계인 찾기"):

    scores = []

    for alien in aliens:
        scores.append((score(alien), alien))

    scores.sort(reverse=True, key=lambda x: x[0])

    match_score, best = scores[0]

    st.balloons()

    st.markdown("---")

    st.markdown(f"# {best['emoji']} {best['name']}")

    st.write(f"### 🌍 출신 행성 : {best['planet']}")

    st.progress(match_score / 100)

    st.metric("❤️ 사랑 매칭률", f"{match_score}%")

    st.write(best["description"])

    reasons = []

    if personality == best["likes"]["personality"]:
        reasons.append("성격이 잘 맞아요.")

    if hobby == best["likes"]["hobby"]:
        reasons.append("취미가 같아요.")

    if date == best["likes"]["date"]:
        reasons.append("데이트 취향이 비슷해요.")

    if adventure == best["likes"]["adventure"]:
        reasons.append("모험심이 비슷해요.")

    if len(reasons) == 0:
        reasons.append("반대 성향이라 서로에게 끌리는 커플이에요!")

    st.subheader("✨ 추천 이유")

    for r in reasons:
        st.write("✅", r)

    st.success(f"{name}님은 **{best['name']}** 과(와) 우주 최고의 커플이 될 가능성이 높습니다! 💕")

    st.markdown("---")

    st.subheader("🏆 매칭 순위")

    for s, alien in scores:
        st.write(f"{alien['emoji']} **{alien['name']}** — {s}%")
