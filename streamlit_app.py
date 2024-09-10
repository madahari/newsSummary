import streamlit as st
import feedparser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import nltk
import ssl
import time

# SSL 인증서 문제 해결
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# NLTK 데이터 다운로드
nltk.download('punkt')

# 뉴스 요약 함수
def summarize_text(text, sentences_count=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return " ".join([str(sentence) for sentence in summary])

# RSS 피드에서 뉴스 가져오기
def get_news(url):
    feed = feedparser.parse(url)
    return feed.entries

# 앱 메인 함수
def main():
    st.title("실시간 뉴스 요약 앱")

    # 사이드바: 뉴스 사이트 및 관심 주제 등록
    st.sidebar.header("설정")
    news_sites = st.sidebar.text_area("뉴스 사이트 RSS 주소 (한 줄에 하나씩)", 
                                      "http://feeds.bbci.co.uk/news/rss.xml\n"
                                      "http://rss.cnn.com/rss/edition.rss")
    topics = st.sidebar.text_input("관심 주제 (쉼표로 구분)", "technology, science, health")

    # 메인 화면: 뉴스 표시
    if st.button("뉴스 업데이트"):
        news_sites = news_sites.split('\n')
        topics = [topic.strip() for topic in topics.split(',')]

        for site in news_sites:
            st.subheader(f"뉴스 출처: {site}")
            try:
                news_items = get_news(site)
                
                for item in news_items:
                    if any(topic.lower() in item.title.lower() for topic in topics):
                        st.write(f"**{item.title}**")
                        try:
                            summary = summarize_text(item.description)
                            st.write(summary)
                        except Exception as e:
                            st.write("요약을 생성하는 데 문제가 발생했습니다.")
                            st.write(item.description)  # 대신 원본 설명을 표시
                        st.write(f"[원문 링크]({item.link})")
                        st.write("---")
            except Exception as e:
                st.error(f"뉴스를 가져오는 데 문제가 발생했습니다: {site}")
                st.error(str(e))

    # 자동 업데이트 (실제 실시간은 아니지만 주기적 업데이트)
    if st.checkbox("자동 업데이트 (30초마다)"):
        while True:
            main()
            time.sleep(30)

if __name__ == "__main__":
    main()
