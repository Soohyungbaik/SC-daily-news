import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import smtplib
from email.mime.text import MIMEText

# 오늘 날짜
today = datetime.today().strftime('%Y-%m-%d')

# 뉴스 소스 URL
source_url = f"https://baik1204.github.io/SC-daily-news/{today}.html"
res = requests.get(source_url)

# 뉴스 없음 처리
if res.status_code == 404:
    print("📭 오늘 뉴스가 아직 없어 빈 뉴스 파일을 생성합니다.")
    os.makedirs("daily_html", exist_ok=True)

    empty_html = f"<html><head><meta charset='UTF-8'><title>{today} 뉴스 없음</title></head><body>"
    empty_html += f"<h2>{today} 뉴스 없음</h2></body></html>"

    with open(f"daily_html/{today}.html", 'w', encoding='utf-8') as f:
        f.write(empty_html)

    html_to_send = empty_html  # 이메일도 빈 내용으로 전송

else:
    # 뉴스 HTML 파싱
    soup = BeautifulSoup(res.text, 'html.parser')
    items = soup.select('li > a')

    # 키워드 불러오기
    with open('keywords.txt', 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]

    # 키워드 필터링
    filtered = [item for item in items if any(k in item.text for k in keywords)]

    # 뉴스 HTML 구성
    html = f"<html><head><meta charset='UTF-8'><title>{today} 뉴스</title></head><body>"
    html += f"<h2>{today} 키워드 뉴스</h2><ul>"

    if not filtered:
        html += "<li>해당 키워드의 뉴스가 없습니다.</li>"
    else:
        for a in filtered:
            html += f"<li><a href='{a['href']}'>{a.text}</a></li>"

    html += "</ul></body></html>"

    # 저장
    os.makedirs("daily_html", exist_ok=True)
    with open(f"daily_html/{today}.html", 'w', encoding='utf-8') as f:
        f.write(html)

    html_to_send = html  # 이메일 전송용 본문

# ✅ index.html 갱신
index_path = "index.html"
if not os.path.exists(index_path):
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(
            "<html>\n"
            "  <head>\n"
            "    <meta charset='UTF-8'>\n"
            "    <title>SC 뉴스 모음</title>\n"
            "  </head>\n"
            "  <body>\n"
            "    <h1>SC 뉴스 모음</h1>\n"
            "    <ul>\n"
            "    </ul>\n"
            "  </body>\n"
            "</html>\n"
        )

with open(index_path, 'r', encoding='utf-8') as f:
    index_html = f.read()

new_entry_tag = f"<li><a href='daily_html/{today}.html'>{today}</a></li>"
if new_entry_tag not in index_html:
    index_html = index_html.replace("</ul>", f"{new_entry_tag}\n</ul>")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)

# ✅ 이메일 전송
msg = MIMEText(html_to_send, 'html')
msg['Subject'] = f"[SC 뉴스레터] {today}"
msg['From'] = os.getenv("EMAIL_FROM")
msg['To'] = os.getenv("EMAIL_TO")

try:
    server = smtplib.SMTP_SSL('smtp.office365.com', 587)
    server.starttls()
    server.login(os.getenv("EMAIL_FROM"), os.getenv("EMAIL_PASSWORD"))
    server.send_message(msg)
    server.quit()
    print("✅ 뉴스레터 이메일 전송 완료")
except Exception as e:
    print("❌ 이메일 전송 실패:", e)

print("✅ 뉴스레터 HTML 생성 완료")

