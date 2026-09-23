from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/news/{company}")
def get_news(company: str):
    articles = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    today_date = datetime.now().strftime("%Y.%m.%d")

    try:
        if company == "jeju":
            # 제주일보 메인 페이지로 변경하여 가장 최신 기사 수집
            url = "http://www.jejunews.com/"
            res = requests.get(url, headers=headers)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for a in soup.select('a'):
                title = a.get_text().strip()
                link = a.get('href', '')
                # 기사 링크 패턴(articleView 또는 idxno)이 포함된 최신 기사만 선별
                if title and len(title) > 10 and ('articleView.html' in link or 'idxno' in link):
                    if link.startswith('http'):
                        pass
                    elif link.startswith('/'):
                        link = "http://www.jejunews.com" + link
                    else:
                        link = "http://www.jejunews.com/" + link
                        
                    articles.append({"title": title, "time": today_date, "link": link})
                    
        elif company == "halla":
            url = "https://m.ihalla.com/"
            res = requests.get(url, headers=headers)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for a in soup.select('a'):
                title = a.get_text().strip()
                link = a.get('href', '')
                if title and len(title) > 10 and 'article' in link:
                    if link.startswith('/'):
                        link = "https://m.ihalla.com" + link
                    elif not link.startswith('http'):
                        continue
                    articles.append({"title": title, "time": today_date, "link": link})
                    
        elif company == "jemin":
            url = "https://www.jemin.com/"
            res = requests.get(url, headers=headers)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            for a in soup.select('a'):
                title = a.get_text().strip()
                link = a.get('href', '')
                if title and len(title) > 10 and ('news' in link or 'article' in link):
                    if link.startswith('/'):
                        link = "https://www.jemin.com" + link
                    elif not link.startswith('http'):
                        continue
                    articles.append({"title": title, "time": today_date, "link": link})

    except Exception as e:
        print(f"크롤링 에러: {e}")

    # 중복 제거 및 상위 10개 추출
    unique_articles = []
    seen_titles = set()
    for art in articles:
        if art["title"] not in seen_titles:
            seen_titles.add(art["title"])
            unique_articles.append(art)
        if len(unique_articles) >= 10:
            break

    if not unique_articles:
        unique_articles = [
            {"title": "기사를 불러오는 중 문제가 발생했습니다. 잠시 후 새로고침 해주세요.", "time": today_date, "link": "#"}
        ]

    return {"articles": unique_articles}
