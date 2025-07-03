import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

# 날짜 설정
today = datetime.today().strftime('%Y-%m-%d')

# SC 뉴스 소스
source_url = f"https://baik1204.github.io/SC-daily-news/{today}.html"
res = requests.get(source_url)

# daily_html 폴더 생성
os.makedirs("daily_html", exist_ok=True)

# 뉴스 없음 처리
if res.status_code == 404:
    print("📭 SC 소스 없음. 뉴스 없음 처리.")
    empty_html = f"<html><head><meta charset='UTF-8'><title>{today} 뉴스 없음</title></head><body><h2>{today} 뉴스 없음</h2></body></html>"
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
        keyword_match = any(k in title for k in keywords) if keywords else False
        media_match = any(m in title or m in url for m in media_list) if media_list else False

        if (not keywords and not media_list) or keyword_match or media_match:
            filtered.append((title, url))

    # 이메일 본문 생성 (다크모드 없음)
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
        html += "<li>설정한 키워드나 매체에 해당하는 뉴스가 없습니다.</li>"
    else:
        for title, url in filtered:
            thumb = f"https://www.google.com/s2/favicons?domain={url}"
            html += f"<li class='item'><img src='{thumb}' class='thumbnail'/><a href='{url}'>{title}</a></li>"

    html += "</ul></body></html>"

    # 저장
    with open(f"daily_html/{today}.html", 'w', encoding='utf-8') as f:
        f.write(html)

    html_to_send = html

    # index.html 갱신
    index_path = "index.html"
    if not os.path.exists(index_path):
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(
                "<html><head><meta charset='UTF-8'><title>SC 뉴스 모음</title></head>"
                "<body><h1>SC 뉴스 모음</h1><ul></ul></body></html>"
            )

    with open(index_path, 'r', encoding='utf-8') as f:
        index_html = f.read()

    new_entry = f"<li><a href='daily_html/{today}.html'>{today}</a></li>"
    if new_entry not in index_html:
        index_html = index_html.replace("</ul>", f"{new_entry}\n</ul>")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_html)

    # 이메일 전송
    msg = MIMEText(html_to_send, 'html')
    msg['Subject'] = f"[SC 뉴스레터] {today}"
    msg['From'] = os.getenv("EMAIL_FROM")
    msg['To'] = os.getenv("EMAIL_TO")

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
        server.send_message(msg)
        server.quit()
        print("✅ 뉴스레터 이메일 전송 완료")
    except Exception as e:
        print("❌ 이메일 전송 실패:", e)

    print("✅ 뉴스레터 HTML 생성 완료")


