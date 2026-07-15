import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울 공영주차장 정보",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울 공영주차장 정보 조회")

uploaded_file = st.file_uploader(
    "서울시 공영주차장 안내 정보.csv 업로드",
    type="csv"
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file, encoding="cp949")

    st.success(f"{len(df)}개의 주차장 정보를 불러왔습니다.")

    # 검색
    keyword = st.text_input("🔍 주차장명 또는 주소 검색")

    if keyword:
        result = df[
            df["주차장명"].astype(str).str.contains(keyword, case=False, na=False)
            |
            df["주소"].astype(str).str.contains(keyword, case=False, na=False)
        ]
    else:
        result = df

    st.write(f"검색 결과 : {len(result)}개")

    # 카드 출력
    for _, row in result.iterrows():

        with st.expander(f"🅿️ {row['주차장명']}"):

            c1, c2 = st.columns(2)

            with c1:
                st.subheader("📍 기본 정보")
                st.write("**주소**", row["주소"])
                st.write("**전화번호**", row["전화번호"])
                st.write("**주차장 종류**", row["주차장 종류명"])
                st.write("**총 주차면수**", f"{row['총 주차면']}면")
                st.write("**무료/유료**", row["유무료구분명"])
                st.write("**야간 무료개방**", row["야간무료개방여부명"])

            with c2:
                st.subheader("💰 요금 정보")
                st.write("**기본 요금**", row["기본 주차 요금"], "원")
                st.write("**기본 시간**", row["기본 주차 시간(분 단위)"], "분")
                st.write("**추가 요금**", row["추가 단위 요금"], "원")
                st.write("**추가 시간**", row["추가 단위 시간(분 단위)"], "분")
                st.write("**1일 최대 요금**", row["일 최대 요금"], "원")
                st.write("**월 정기권 금액**", row["월 정기권 금액"], "원")

            st.divider()

            st.subheader("🕒 운영시간")

            st.write(
                f"평일 : {row['평일 운영 시작시각(HHMM)']} ~ {row['평일 운영 종료시각(HHMM)']}"
            )

            st.write(
                f"주말 : {row['주말 운영 시작시각(HHMM)']} ~ {row['주말 운영 종료시각(HHMM)']}"
            )

            st.write(
                f"공휴일 : {row['공휴일 운영 시작시각(HHMM)']} ~ {row['공휴일 운영 종료시각(HHMM)']}"
            )

    st.divider()

    st.subheader("📋 전체 목록")

    st.dataframe(
        result[
            [
                "주차장명",
                "주소",
                "전화번호",
                "기본 주차 요금",
                "일 최대 요금",
                "총 주차면",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

else:
    st.info("CSV 파일을 업로드하세요.")

    st.info("왼쪽에서 CSV 파일을 업로드해주세요.")
