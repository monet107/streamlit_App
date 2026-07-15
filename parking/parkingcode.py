import streamlit as st
import pandas as pd

# ------------------------
# 페이지 설정
# ------------------------
st.set_page_config(
    page_title="서울 공영주차장 정보",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울 공영주차장 정보 조회")
st.markdown("서울시 공영주차장 정보를 검색하고 요금을 확인할 수 있습니다.")

# ------------------------
# CSV 업로드
# ------------------------
uploaded_file = st.file_uploader(
    "📂 서울시 공영주차장 안내 정보.csv 업로드",
    type="csv"
)

if uploaded_file is not None:

    # CP949 인코딩
    df = pd.read_csv(uploaded_file, encoding="cp949")

    st.success(f"총 {len(df)}개의 주차장 정보를 불러왔습니다.")

    # ------------------------
    # 검색
    # ------------------------

    keyword = st.text_input(
        "🔍 주차장명 또는 주소 검색"
    )

    if keyword:
        result = df[
            df["주차장명"].astype(str).str.contains(keyword, case=False, na=False)
            |
            df["주소"].astype(str).str.contains(keyword, case=False, na=False)
        ]
    else:
        result = df

    st.write(f"검색 결과 : **{len(result)}개**")

    # ------------------------
    # 카드 형태 출력
    # ------------------------

    for _, row in result.iterrows():

        with st.expander(f"🅿️ {row['주차장명']}"):

            left, right = st.columns(2)

            with left:

                st.markdown("### 📍 기본정보")

                st.write("**주소**")
                st.write(row["주소"])

                st.write("**전화번호**")
                st.write(row["전화번호"])

                st.write("**주차장 종류**")
                st.write(row["주차장 종류"])

                st.write("**총 주차면수**")
                st.write(f"{row['총 주차면']}면")

            with right:

                st.markdown("### 💰 요금정보")

                st.write("**기본 주차 요금**")
                st.write(row["기본 주차 요금"])

                st.write("**추가 단위 요금**")
                st.write(row["추가 단위 요금"])

                st.write("**1일 최대 요금**")
                st.write(row["일 최대 요금"])

                st.write("**월 정기권 요금**")
                st.write(row["월 정기권 요금"])

            st.divider()

            st.markdown("### 🕒 운영시간")

            st.write(
                f"평일 : {row['평일 운영 시작시각(HHMM)']} ~ {row['평일 운영 종료시각(HHMM)']}"
            )

            st.write(
                f"토요일 : {row['토요일 운영 시작시각(HHMM)']} ~ {row['토요일 운영 종료시각(HHMM)']}"
            )

            st.write(
                f"공휴일 : {row['공휴일 운영 시작시각(HHMM)']} ~ {row['공휴일 운영 종료시각(HHMM)']}"
            )

    st.divider()

    st.subheader("📋 전체 데이터")

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("왼쪽에서 CSV 파일을 업로드해주세요.")
