import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울 공영주차장 정보",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울 공영주차장 정보 조회")
st.write("CSV 파일을 업로드하면 지역별 주차장 정보를 조회할 수 있습니다.")

uploaded_file = st.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)

if uploaded_file:

    # CSV 읽기
    try:
        df = pd.read_csv(uploaded_file, encoding="utf-8")
    except:
        df = pd.read_csv(uploaded_file, encoding="cp949")

    st.success(f"{len(df)}개의 주차장 정보를 불러왔습니다.")

    # 검색창
    keyword = st.text_input("🔍 주차장명 또는 주소 검색")

    if keyword:
        result = df[
            df["주차장명"].astype(str).str.contains(keyword, case=False, na=False)
            |
            df["주소"].astype(str).str.contains(keyword, case=False, na=False)
        ]
    else:
        result = df

    st.subheader("검색 결과")

    if len(result) == 0:
        st.warning("검색 결과가 없습니다.")
    else:
        for _, row in result.iterrows():

            with st.expander(f"🅿️ {row['주차장명']}"):

                col1, col2 = st.columns(2)

                with col1:
                    st.write("**주소**")
                    st.write(row["주소"])

                    if "전화번호" in df.columns:
                        st.write("**전화번호**")
                        st.write(row["전화번호"])

                    if "운영시간" in df.columns:
                        st.write("**운영시간**")
                        st.write(row["운영시간"])

                with col2:
                    if "기본주차요금" in df.columns:
                        st.write("**기본요금**")
                        st.write(row["기본주차요금"])

                    if "추가단위요금" in df.columns:
                        st.write("**추가요금**")
                        st.write(row["추가단위요금"])

                    if "일최대요금" in df.columns:
                        st.write("**1일 최대요금**")
                        st.write(row["일최대요금"])

    st.subheader("📋 전체 데이터")
    st.dataframe(result, use_container_width=True)

else:
    st.info("왼쪽에서 CSV 파일을 업로드해주세요.")
    st.info("왼쪽의 'Browse files' 버튼을 눌러 CSV를 업로드하세요.")
