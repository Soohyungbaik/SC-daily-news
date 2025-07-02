import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# 오늘 날짜 기준
today = datetime.today().strftime('%Y-%m-%d')
url = f"https://baik1204.github.io/SC-daily-news/{today}.html"

res = requests.get(url)
if res.status_code == 404:
    print("소스 뉴스가 아직 없습니다.")
    exit()

soup = BeautifulSoup(res.text, 'html.parser')
items = soup.select('li > a')

with open('keywords.txt', 'r', encoding='utf-8') as f:
    keywords = [line.strip() for line in f.readlines() if line.strip()]

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

# HTML 저장
os.makedirs("daily_html", exist_ok=True)
with open(f"daily_html/{today}.html", 'w', encoding='utf-8') as f:
    f.write(html)

# index.html 업데이트
index_path = "index.html"
if os.path.exists(index_path):
    with open(index_path, 'r', encoding='utf-8') as f:
        index_html = f.read()
else:
    index_html = "<html><body><h1>SC 뉴스 모음</h1><ul>"

new_entry = f"<li><a href='daily_html/{today}.html'>{today}</a></li>\n"
if new_entry not in index_html:
    index_html = index_html.replace("</ul>", f"{new_entry}</ul>")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)

# 이메일 발송 (선택사항)
from email.mime.text import MIMEText
import smtplib

content = html
msg = MIMEText(content, 'html')
msg['Subject'] = f"[SC 뉴스레터] {today}"
msg['From'] = os.getenv("EMAIL_FROM")
msg['To'] = os.getenv("EMAIL_TO")

server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
server.send_message(msg)
server.quit()
index_path = "index.html"

if not os.path.exists(index_path):
    # index.html이 없으면 새로 생성
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write("<html><head><meta charset='UTF-8'></head><body><h1>SC 뉴스 모음</h1><ul></ul></body></html>")
    
    # 조건부 커밋
    if [ -f "index.html" ] || [ "$(ls daily_html 2>/dev/null)" ]; then
      git add index.html daily_html || true
      git commit -m "📰 Add daily newsletter" || echo "Nothing to commit"
      git push
    else
      echo "No new files to commit."
    fi
