import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

# 오늘 날짜
today = datetime.today().strftime('%Y-%m-%d')

# 소스 뉴스 페이지 주소
source_url = f"https://baik1204.github.io/SC-daily-news/{today}.html"
res = requests.get(source_url)

# daily_html 폴더 생성
os.makedirs("daily_html", exist_ok=True)

# 404인 경우: 뉴스 없음 처리
if res.status_code == 404:
    print("📭 오늘 뉴스가 아직 없어 빈 뉴스 파일을 생성합니다.")
    empty_html = f"""
    <html><head><meta charset='UTF-8'><title>{today} 뉴스 없음</title></head>
    <body><h2>{today} 뉴스 없음</h2></body></html>
    """
    with open(f"daily_html/{today}.html", 'w', encoding='utf-8') as f:
        f.write(empty_html)
    html_to_send = empty_html
else:
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.select('li > a')

    # 키워드 불러오기
    if os.path.exists('keywords.txt'):
        with open('keywords.txt', 'r', encoding='utf-8') as f:
            keywords = [line.strip() for line in f if line.strip()]
    else:
        keywords = []

    # 매체 리스트 불러오기
    if os.path.exists('media_list.txt'):
        with open('media_list.txt', 'r', encoding='utf-8') as f:
            media_list = [line.strip() for line in f if line.strip()]
    else:
        media_list = []

    # 필터링 조건
    filtered = []
    for item in items:
        title = item.text
        url = item['href']
        if (not keywords or any(k in title for k in keywords)) and \
           (not media_list or any(m in url for m in media_list)):
            filtered.append((title, url))

    # 이메일용 HTML 본문 구성 (썸네일 + 다크모드 대응)
    html = f"""
    <html>
    <head>
      <meta charset='UTF-8'>
      <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #fff;
          color: #000;
        }}
        @media (prefers-color-scheme: dark) {{
          body {{
            background-color: #121212;
            color: #e0e0e0;
          }}
          a {{ color: #80cbc4; }}
        }}
        .item {{
          margin-bottom: 15px;
        }}
        .thumbnail {{
          width: 100px;
          height: auto;
          margin-right: 10px;
          vertical-align: middle;
        }}
      </style>
    </head>
    <body>
      <h2>[SC 뉴스레터] {today}</h2>
      <ul>
    """

    if not filtered:
        html += "<li>해당 키워드 및 매체 조건에 맞는 뉴스가 없습니다.</li>"
    else:
        for title, url in filtered:
            # 간이 썸네일


