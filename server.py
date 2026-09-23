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
            # 제주일보 최신 전체 기사 목록 페이지 타겟팅
            url = "http://www.jejunews.com/news/articleList.html?sc_section_code=S1N1&view_type=sm"
            res = requests.get(url, headers=headers, timeout=5)
            res.encoding = 'utf-8'
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 제주일보 기사 리스트 구조(section 하위 기사 아이템)에서 정확히 추출
            item_list = soup.select('.section-article-list .list-block, .default-list li, ul li')
            
            for item in item_list:
                a_tag = item.find('a')
                if not a_tag:
                    continue
                title = a_tag.get_text().strip()
                link = a_tag.get('href', '')
                
                # 날짜 정보가 있다면 추출 시도, 없으면 오늘 날짜
                date_elem = item.select_text('.date') if hasattr(item, 'select_text') else None
                art_time = today_date
                
                if title and len(title) > 8 and 'articleView.html' in link:
                    if link.startswith('/'):
                        link = "http://www.jejunews.com" + link
                    elif not link.startswith('http'):
                        link = "http://www.jejunews.com/news/" + link
                        
                    articles.append({"title": title, "time": art_time, "link": link})
            
            # 만약 위 셀렉터로 안 잡히면 일반 a 태그 탐색 (단, 오래된 고정 메뉴 제외)
            if not articles:
                for a in soup.select('a'):
                    title = a.get_text().strip()
                    link = a.get('href', '')
                    if title and len(title) > 10 and 'articleView.html' in link:
                        if 'sc_sub_section_code' in link: # 기획/연도별 코너 제외
                            continue
                        if link.startswith('/'):
                            link = "http://www.jejunews.com" + link
                        articles.append({"title": title, "time": today_date, "link": link})

        elif company == "halla":
            url = "https://m.ihalla.com/"
            res = requests.get(url, headers=headers, timeout=5)
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
            res = requests.get(url, headers=headers, timeout=5)
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
            {"title": f"[{company.upper}] 실시간 기사를 불러오는 중입니다.", "time": today_date, "link": "#"}
        ]

    return {"articles": unique_articles}
