import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

# 오늘 날짜 설정
today = datetime.today().strftime('%Y-%m-%d')

# 원본 뉴스 소스 (so247)
source_url = f"https://baik1204.github.io/SC-daily-news/{today}.html"
res = requests.get(source_url)

if res.status_code == 404:
    print("📭 오늘 뉴스가 아직 올라오지 않았습니다.")
    exit()

# 뉴스 파싱
soup = BeautifulSoup(res.text, 'html.parser')
items = soup.select('li > a')

# 키워드 불러오기
with open('keywords.txt', 'r', encoding='utf-8') as f:
    keywords = [line.strip() for line in f if line.strip()]

# 키워드 필터링
filtered = [item for item in items if any(k in item.text for k in keywords)]

# HTML 생성
html = f"<html><head><meta charset='UTF-8'><title>{today} 뉴스</title></head><body>"
html += f"<h2>{today} 키워드 뉴스</h2><ul>"

if not filtered:
    html += "<li>해당 키워드의 뉴스가 없습니다.</li>"
else:
    for a in filtered:
        html += f"<li><a href='{a['href']}'>{a.text}</a></li>"

html += "</ul></body></html>"

# 결과 저장 폴더
os.makedirs("daily_html", exist_ok=True)

# daily_html/{날짜}.html 저장
with open(f"daily_html/{today}.html", 'w', encoding='utf-8') as f:
    f.write(html)

# index.html 갱신
index_path = "index.html"
if not os.path.exists(index_path):
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("<html><head><meta charset='UTF-8'></head><body><h1>SC 뉴스 모음</h1><ul></ul></body></html>")

with open(index_path, 'r', encoding='utf-8') as f:
    index_html = f.read()

new_entry = f"<li><a href='daily_html/{today}.html'>{today}</a></li>\n"
if new_entry not in index_html:
    index_html = index_html.replace("</ul>", f"{new_entry}</ul>")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)

# 이메일 발송
msg = MIMEText(html, 'html')
msg['Subject'] = f"[SC 뉴스레터] {today}"
msg['From'] = os.getenv("EMAIL_FROM")
msg['To'] = os.getenv("EMAIL_TO")

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
server.send_message(msg)
server.quit()

print("✅ 뉴스레터 HTML 생성 및 이메일 발송 완료")

from datetime import datetime

# 오늘 날짜를 YYYY-MM-DD 형식으로 가져옴
today = datetime.today().strftime("%Y-%m-%d")

# index.html 파일을 생성 또는 덮어쓰기
with open("index.html", "w", encoding="utf-8") as f:
    f.write(f"""
    <html>
      <head>
        <meta charset="UTF-8">
        <title>SC 뉴스 모음</title>
      </head>
      <body>
        <h1>SC 뉴스 모음</h1>
        <ul>
          <li><a href="daily_html/{today}.html">{today}</a></li>
        </ul>
      </body>
    </html>
    """)

