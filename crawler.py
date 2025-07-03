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

    # 키워드 & 매체 불러오기
    with open('keywords.txt', 'r', encoding='utf-8') as f:
        keywords = [line.strip() for line in f if line.strip()]
    with open('media_list.txt', 'r', encoding='utf-8') as f:
        media_list = [line.strip() for line in f if line.strip()]

    # 필터링: 키워드 + 매체
    filtered = [
        item for item in items
        if any(k in item.text for k in keywords)
        and any(m in item.text or m in item['href'] for m in media_list)
    ]

    # 썸네일 추출 (가능한 경우)
    def get_og_image(url):
        try:
            r = requests.get(url, timeout=5)
            s = BeautifulSoup(r.text, 'html.parser')
            og_img = s.find("meta", property="og:image")
            return og_img['content'] if og_img else None
        except:
            return None

    # 본문 구성
    html = f"""
    <html>
      <head>
        <meta charset='UTF-8'>
        <meta name="color-scheme" content="light dark">
        <style>
          body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            padding: 20px;
            color: #333;
          }}
          @media (prefers-color-scheme: dark) {{
            body {{
              background-color: #121212;
              color: #e0e0e0;
            }}
            a {{ color: #90caf9; }}
          }}
          .container {{
            background-color: #ffffff;
            padding: 20px;
            border-radius: 8px;
            max-width: 700px;
            margin: auto;
            box-shadow: 0 0 10px rgba(0,0,0,0.05);
          }}
          h2 {{ color: #333; }}
          .card {{
            border-bottom: 1px solid #ddd;
            padding: 10px 0;
            display: flex;
            gap: 10px;
            align-items: center;
          }}
          .thumb {{
            width: 100px;
            height: 70px;
            object-fit: cover;
            border-radius: 6px;
          }}
          .footer {{
            font-size: 12px;
            color: #888;
            margin-top: 30px;
          }}
        </style>
      </head>
      <body>
        <div class="container">
          <h2>📰 {today} 뉴스 요약</h2>
    """

    if not filtered:
        html += "<p>해당 키워드와 매체에 해당하는 뉴스가 없습니다.</p>"
    else:
        for a in filtered:
            link = a['href']
            title = a.text
            thumb = get_og_image(link)
            html += "<div class='card'>"
            if thumb:
                html += f"<img class='thumb' src='{thumb}' alt='thumb'>"
            html += f"<div><a href='{link}' target='_blank'>{title}</a></div>"
            html += "</div>"

    html += f"""
          <div class="footer">
            이 뉴스레터는 GitHub Actions로 매일 자동 발송됩니다.<br>
            키워드와 매체는 keywords.txt, media_list.txt를 기준으로 필터링됩니다.
          </div>
        </div>
      </body>
    </html>
    """

    os.makedirs("daily_html", exist_ok=True)
    with open(f"daily_html/{today}.html", 'w', encoding='utf-8') as f:
        f.write(html)

    html_to_send = html

# index.html 갱신
index_path = "index.html"
if not os.path.exists(index_path):
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(
            "<html>\n<head><meta charset='UTF-8'><title>SC 뉴스 모음</title></head>\n"
            "<body><h1>SC 뉴스 모음</h1><ul></ul></body>\n</html>"
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

