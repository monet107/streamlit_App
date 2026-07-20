import streamlit as st
import pandas as pd
import re
from googleapiclient.discovery import build
from kiwipiepy import Kiwi
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
from datetime import datetime

# 페이지 기본 설정
st.set_page_config(page_title="유튜브 댓글 분석기", layout="wide")
st.title("📊 유튜브 댓글 분석기 (YouTube Comment Analyzer)")
st.caption("유튜브 영상 링크를 입력하고 댓글 반응도와 워드클라우드를 확인해보세요!")


# --- 1. 유튜브 API 설정 및 함수 정의 ---
# 스트림릿 Secrets에서 안전하게 키를 불러옵니다.
if "YOUTUBE_API_KEY" in st.secrets:
    api_key = st.secrets["YOUTUBE_API_KEY"]
else:
    st.error("❌ 스트림릿 Settings -> Secrets에 'YOUTUBE_API_KEY'를 설정해 주세요.")
    st.stop()

def extract_video_id(url):
    """유튜브 URL에서 Video ID를 추출하는 함수"""
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_comments(video_id, max_count, api_key):
    """유튜브 댓글을 가져오는 함수"""
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(max_count, 100), # 한 번 요청에 최대 100개
            textFormat="plainText"
        )
        
        while request and len(comments) < max_count:
            response = request.execute()
            for item in response['items']:
                comment_data = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment_data['authorDisplayName'],
                    'text': comment_data['textDisplay'],
                    'like_count': comment_data['likeCount'],
                    'published_at': comment_data['publishedAt']
                })
                if len(comments) >= max_count:
                    break
                    
            # 다음 페이지가 있으면 계속 가져옴
            if 'nextPageToken' in response and len(comments) < max_count:
                request = youtube.commentThreads().list_next(request, response)
            else:
                break
                
        return pd.DataFrame(comments)
    except Exception as e:
        st.error(f"데이터를 가져오는 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# --- 2. UI 및 입력부 ---
video_url = st.text_input("유튜브 영상 링크(URL)를 입력하세요:", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
max_comments = st.slider("가져올 댓글 개수를 설정하세요:", min_value=10, max_value=1000, value=100, step=10)

if st.button("🚀 댓글 분석 시작") and api_key:
    video_id = extract_video_id(video_url)
    
    if not video_id:
        st.error("올바른 유튜브 링크가 아닙니다. URL을 다시 확인해 주세요.")
    else:
        # 영상 임베드 표시
        st.subheader("📺 대상 영상")
        st.video(video_url)
        
        with st.spinner("유튜브에서 댓글을 열심히 긁어오는 중... 🏃‍♂️"):
            df = get_youtube_comments(video_id, max_comments, api_key)
            
        if df.empty:
            st.warning("가져온 댓글이 없습니다. 영상 ID나 API 키를 다시 확인해 주세요.")
        else:
            st.success(f"총 {len(df)}개의 댓글을 성공적으로 가져왔습니다!")
            
            # 데이터 전처리
            df['published_at'] = pd.to_datetime(df['published_at'])
            df['date_hour'] = df['published_at'].dt.strftime('%Y-%m-%d %H:00')
            
            # --- 레이아웃 분할 ---
            col1, col2 = st.columns(2)
            
            # 1. 시간대별 댓글 작성 추이 (Plotly 사용)
            with col1:
                st.subheader("📈 시간대별 댓글 작성 추이")
                time_counts = df.groupby('date_hour').size().reset_index(name='count')
                time_counts = time_counts.sort_values('date_hour')
                
                fig_time = px.line(time_counts, x='date_hour', y='count', title="시간대별 댓글수 변화",
                                   labels={'date_hour': '날짜/시간', 'count': '댓글 수'}, markers=True)
                fig_time.update_xaxes(tickangle=45)
                st.plotly_chart(fig_time, use_container_width=True)
                
            # 2. 댓글 반응도 분석 (좋아요 수 기준 Top 5)
            with col2:
                st.subheader("🔥 가장 반응이 뜨거운 댓글 (Top 5)")
                top_likes = df.nlargest(5, 'like_count')[['author', 'like_count', 'text']]
                
                for idx, row in top_likes.iterrows():
                    st.markdown(f"**👤 {row['author']}** (👍 {row['like_count']}개)")
                    st.info(row['text'])
            
            st.divider()
            
            # 3. 한글 워드클라우드 생성
            st.subheader("🔤 댓글 한글 키워드 워드클라우드")
            
            with st.spinner("한글 형태소를 분석하여 워드클라우드를 생성하고 있습니다..."):
                # Kiwi 형태소 분석기 초기화
                kiwi = Kiwi()
                
                # 명사 추출 함수 (2글자 이상)
                def extract_nouns(text):
                    if not text:
                        return []
                    # 영문, 특수문자 제거 후 한글 위주 추출
                    nouns = []
                    for token in kiwi.tokenize(str(text)):
                        if token.tag.startswith('N') and len(token.form) > 1: # 명사 계열이면서 2글자 이상
                            nouns.append(token.form)
                    return nouns

                # 전체 댓글에서 명사 추출
                all_nouns = []
                for txt in df['text']:
                    all_nouns.extend(extract_nouns(txt))
                    
                if not all_nouns:
                    st.warning("워드클라우드를 생성할 만큼 충분한 한글 명사 단어가 없습니다.")
                else:
                    # 단어 빈도수 사전 생성
                    word_counts = pd.Series(all_nouns).value_counts().to_dict()
                    
                    # 워드클라우드 생성 (스트림릿 클라우드는 기본 나눔 폰트가 없을 수 있으므로 시스템 기본 폰트 경로 지정 필요)
                    # 리눅스 환경(Streamlit Cloud)에서는 보통 DroidSansFallback 등이 잡히나, 폰트 미지정 시 깨짐 방지를 위해 처리
                    try:
                        # 리눅스 우분투 기본 폰트 경로 예시
                        font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf' 
                        wc = WordCloud(font_path=font_path, width=800, height=400, 
                                       background_color='white', max_words=100).generate_from_frequencies(word_counts)
                    except:
                        # 폰트 로드 실패 시 기본 폰트로 시도 (한글이 깨질 수 있어 알림 띄움)
                        wc = WordCloud(width=800, height=400, background_color='white', max_words=100).generate_from_frequencies(word_counts)
                    
                    # 시각화 출력
                    fig_wc, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig_wc)
            
            # 데이터 원본 확인용 테이블
            st.divider()
            st.subheader("📋 수집된 댓글 데이터 원본")
            st.dataframe(df[['author', 'published_at', 'like_count', 'text']], use_container_width=True)

def get_youtube_comments(video_id, max_count, api_key):
    youtube = build('youtube', 'v3', developerKey=api_key)
    comments = []
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(max_count, 100),
            textFormat="plainText"
        )
        
        while request and len(comments) < max_count:
            response = request.execute()
            for item in response['items']:
                comment_data = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'author': comment_data['authorDisplayName'],
                    'text': comment_data['textDisplay'],
                    'like_count': comment_data['likeCount'],
                    'published_at': comment_data['publishedAt']
                })
                if len(comments) >= max_count:
                    break
                    
            if 'nextPageToken' in response and len(comments) < max_count:
                request = youtube.commentThreads().list_next(request, response)
            else:
                break
                
        return pd.DataFrame(comments)
        
