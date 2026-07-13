import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="서울 맞춤 도시 추천",
    page_icon="🏙️",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main{
        background:#F5F7FA;
    }

    .title{
        text-align:center;
        font-size:42px;
        font-weight:bold;
        color:#1f77b4;
    }

    .sub{
        text-align:center;
        color:gray;
        font-size:18px;
    }

    .result{
        background:white;
        padding:25px;
        border-radius:15px;
        box-shadow:0px 0px 15px rgba(0,0,0,0.1);
    }

    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='title'>🏙️ 서울 맞춤 도시 추천</div>", unsafe_allow_html=True)

st.markdown(
"<div class='sub'>당신의 라이프스타일에 맞는 서울 자치구를 추천합니다.</div>",
unsafe_allow_html=True)

df = pd.read_csv("district_data.csv")

features = [
    "공원",
    "안전",
    "교통",
    "보행환경",
    "재정자립도"
]

st.divider()

st.header("🎯 중요도를 순서대로 선택하세요")

rank1 = st.selectbox("1순위", features)
rank2 = st.selectbox("2순위", [x for x in features if x!=rank1])
rank3 = st.selectbox("3순위", [x for x in features if x not in [rank1,rank2]])
rank4 = st.selectbox("4순위", [x for x in features if x not in [rank1,rank2,rank3]])
rank5 = st.selectbox("5순위", [x for x in features if x not in [rank1,rank2,rank3,rank4]])

weights = {
    rank1:5,
    rank2:4,
    rank3:3,
    rank4:2,
    rank5:1
}

if st.button("✨ 도시 추천받기", use_container_width=True):

    score = (
        df[rank1]*5+
        df[rank2]*4+
        df[rank3]*3+
        df[rank4]*2+
        df[rank5]*1
    )

    df["점수"] = score

    result = df.sort_values("점수",ascending=False)

    best = result.iloc[0]

    st.divider()

    st.success(f"🏆 당신에게 가장 잘 맞는 도시는 **{best['구']}** 입니다!")

    col1,col2 = st.columns([1,1])

    with col1:

        fig = px.bar(
            x=features,
            y=[best[f] for f in features],
            color=[best[f] for f in features],
            title="추천 도시 특성"
        )

        st.plotly_chart(fig,use_container_width=True)

    with col2:

        st.metric("추천 도시",best["구"])
        st.metric("적합도",f"{best['점수']/15:.1f}%")

        st.write("### 🥇 TOP3")

        top3=result.head(3)

        st.dataframe(
            top3[["구","점수"]],
            hide_index=True,
            use_container_width=True
        )

        st.write("### 📊 상세 점수")

        for f in features:
            st.progress(int(best[f]))
            st.write(f"{f} : {best[f]}")
