import streamlit as st
import pandas as pd
import re
import os
import urllib.request
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

# [귀찮음 해결] 실행 시 인터넷에서 한글 폰트를 자동으로 다운로드하는 함수
@st.cache_data
def download_font():
    font_url = "https://github.com/naver/nanumfont/raw/master/expanded/NanumGothic.ttf"
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        urllib.request.urlretrieve(font_url, font_path)
    return font_path

# 폰트 다운로드 실행
font_path = download_font()

# --- 1. 유튜브 API 설정 및 함수 정의 ---
st.sidebar.header("⚙️ 설정")

if "YOUTUBE_API_KEY" in st.secrets:
    raw_api_key = st.secrets["YOUTUBE_API_KEY"]
else:
    st.sidebar.error("❌ 스트림릿 Secrets에 'YOUTUBE_API_KEY'를 설정해 주세요.")
    st.stop()

api_key = None
if raw_api_key:
    match = re.search(r'["\'](.*?)["\']', raw_api_key)
    if match:
        api_key = match.group(1).strip()
    elif "=" in raw_api_key:
        api_key = raw_api_key.split("=")[-1].replace('"', '').replace("'", "").strip()
    else:
        api_key = raw_api_key.strip()

def extract_video_id(url):
    pattern = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

def get_youtube_comments(video_id, max_count, api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        comments = []
        
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
        
    except Exception as e:
        if "commentsDisabled" in str(e):
            st.error("🔒 입력하신 영상은 유튜브 내에서 댓글 기능이 비활성화(댓글 중지)된 상태입니다.")
        elif "API key not valid" in str(e):
            st.error("❌ 입력한 YouTube API Key가 올바르지 않습니다.")
        else:
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
        st.subheader("📺 대상 영상")
        st.video(video_url)
        
        with st.spinner("유튜브에서 댓글을 열심히 긁어오는 중... 🏃‍♂️"):
            df = get_youtube_comments(video_id, max_comments, api_key)
            
        if df.empty:
            pass
        else:
            st.success(f"총 {len(df)}개의 댓글을 성공적으로 가져왔습니다!")
            
            df['published_at'] = pd.to_datetime(df['published_at'])
            df['date_hour'] = df['published_at'].dt.strftime('%Y-%m-%d %H:00')
            
            col1, col2 = st.columns(2)
            
            # 1. 시간대별 댓글 작성 추이
            with col1:
                st.subheader("📈 시간대별 댓글 작성 추이")
                time_counts = df.groupby('date_hour').size().reset_index(name='count')
                time_counts = time_counts.sort_values('date_hour')
                
                fig_time = px.line(time_counts, x='date_hour', y='count', title="시간대별 댓글수 변화",
                                   labels={'date_hour': '날짜/시간', 'count': '댓글 수'}, markers=True)
                fig_time.update_xaxes(tickangle=45)
                st.plotly_chart(fig_time, use_container_width=True)
                
            # 2. 댓글 반응도 분석
            with col2:
                st.subheader("🔥 가장 반응이 뜨거운 댓글 (Top 5)")
                top_likes = df.nlargest(5, 'like_count')[['author', 'like_count', 'text']]
                
                for idx, row in top_likes.iterrows():
                    st.markdown(f"**👤 {row['author']}** (👍 {row['like_count']}개)")
                    st.info(row['text'])
            
            st.divider()
            
            # 3. 한글 워드클라우드 생성 (자동 다운로드한 폰트 적용)
            st.subheader("🔤 댓글 한글 키워드 워드클라우드")
            
            with st.spinner("한글 형태소를 분석하여 워드클라우드를 생성하고 있습니다..."):
                kiwi = Kiwi()
                
                def extract_nouns(text):
                    if not text:
                        return []
                    nouns = []
                    for token in kiwi.tokenize(str(text)):
                        if token.tag.startswith('N') and len(token.form) > 1:
                            nouns.append(token.form)
                    return nouns

                all_nouns = []
                for txt in df['text']:
                    all_nouns.extend(extract_nouns(txt))
                    
                if not all_nouns:
                    st.warning("워드클라우드를 생성할 만큼 충분한 한글 명사 단어가 없습니다.")
                else:
                    word_counts = pd.Series(all_nouns).value_counts().to_dict()
                    
                    # 자동 다운로드된 폰트 경로 주입
                    wc = WordCloud(font_path=font_path, width=800, height=400, 
                                   background_color='white', max_words=100).generate_from_frequencies(word_counts)
                    
                    fig_wc, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wc, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig_wc)
            
            st.divider()
            st.subheader("📋 수집된 댓글 데이터 원본")
            st.dataframe(df[['author', 'published_at', 'like_count', 'text']], use_container_width=True)
