import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from loguru import logger
import time
import re

# 로깅 설정
logger.add("yes24/data/scraping_{time}.log", rotation="500 MB")

def scrape_yes24_books():
    """
    Yes24 웹사이트에서 특정 카테고리의 도서 정보를 수집합니다.
    """
    logger.info("Yes24 도서 데이터 수집 시작")

    url = "https://www.yes24.com/product/category/CategoryProductContents"
    
    # 요청 헤더 설정 (agent_scraping.md 명세 참고)
    headers = {
        "host": "www.yes24.com",
        "referer": "https://www.yes24.com/product/category/display/001001003032",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }

    # 페이로드 설정 (agent_scraping.md 명세 참고)
    # page를 1부터 3까지 수집하도록 설정 (예시로 3페이지까지만)
    all_books = []
    
    for page in range(1, 4):
        logger.info(f"페이지 {page} 수집 중...")
        params = {
            "dispNo": "001001003032",
            "order": "SINDEX_ONLY",
            "addOptionTp": "0",
            "page": str(page),
            "size": "24",
            "statGbYn": "N",
            "viewMode": "",
            "_options": "",
            "directDelvYn": "",
            "usedTp": "0",
            "elemNo": "0",
            "elemSeq": "0",
            "seriesNumber": "0"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('div.itemUnit')
            
            if not items:
                logger.warning(f"페이지 {page}에서 도서 정보를 찾을 수 없습니다.")
                break
                
            for item in items:
                try:
                    # 도서명 및 부제
                    info_name = item.select_one('div.info_name')
                    title = info_name.select_one('a.gd_name').get_text(strip=True) if info_name.select_one('a.gd_name') else ""
                    subtitle = info_name.select_one('span.gd_nameE').get_text(strip=True) if info_name.select_one('span.gd_nameE') else ""
                    
                    # 저자, 출판사, 출판일
                    info_pubGrp = item.select_one('div.info_pubGrp')
                    author = info_pubGrp.select_one('span.info_auth').get_text(strip=True).replace(" 저", "") if info_pubGrp.select_one('span.info_auth') else ""
                    publisher = info_pubGrp.select_one('span.info_pub').get_text(strip=True) if info_pubGrp.select_one('span.info_pub') else ""
                    pub_date = info_pubGrp.select_one('span.info_date').get_text(strip=True) if info_pubGrp.select_one('span.info_date') else ""
                    
                    # 가격 정보
                    info_price = item.select_one('div.info_price')
                    discount_rate = info_price.select_one('span.txt_sale em.num').get_text(strip=True) if info_price.select_one('span.txt_sale em.num') else "0"
                    sale_price = info_price.select_one('strong.txt_num em.yes_b').get_text(strip=True).replace(",", "") if info_price.select_one('strong.txt_num em.yes_b') else "0"
                    original_price = info_price.select_one('span.txt_num.dash em.yes_m').get_text(strip=True).replace(",", "") if info_price.select_one('span.txt_num.dash em.yes_m') else sale_price
                    
                    # 판매지수, 리뷰, 평점
                    info_rating = item.select_one('div.info_rating')
                    sales_index_text = info_rating.select_one('span.saleNum').get_text(strip=True) if info_rating.select_one('span.saleNum') else ""
                    sales_index = re.sub(r'[^0-9]', '', sales_index_text) if sales_index_text else "0"
                    
                    review_count_text = info_rating.select_one('span.rating_rvCount em.txC_blue').get_text(strip=True) if info_rating.select_one('span.rating_rvCount em.txC_blue') else "0"
                    review_count = re.sub(r'[^0-9]', '', review_count_text)
                    
                    rating = info_rating.select_one('span.rating_grade em.yes_b').get_text(strip=True) if info_rating.select_one('span.rating_grade em.yes_b') else "0"
                    
                    # 태그 수집 (예시: #파이썬, #AI 등)
                    tags = [tag.get_text(strip=True) for tag in item.select('div.info_tag span.tag a')]
                    
                    book_data = {
                        "title": title,
                        "subtitle": subtitle,
                        "author": author,
                        "publisher": publisher,
                        "pub_date": pub_date,
                        "discount_rate": int(discount_rate) if discount_rate.isdigit() else 0,
                        "sale_price": int(sale_price) if sale_price.isdigit() else 0,
                        "original_price": int(original_price) if original_price.isdigit() else 0,
                        "sales_index": int(sales_index) if sales_index.isdigit() else 0,
                        "review_count": int(review_count) if review_count.isdigit() else 0,
                        "rating": float(rating) if rating.replace('.', '', 1).isdigit() else 0.0,
                        "tags": ", ".join(tags)
                    }
                    all_books.append(book_data)
                    
                except Exception as e:
                    logger.error(f"아이템 파싱 중 오류 발생: {e}")
                    continue
            
            # 사이트 부하 방지를 위해 잠깐 대기
            time.sleep(1)
            
        except requests.RequestException as e:
            logger.error(f"요청 중 에러 발생: {e}")
            break

    # 데이터프레임 생성 및 CSV 저장
    if all_books:
        df = pd.DataFrame(all_books)
        os.makedirs("yes24/data", exist_ok=True)
        save_path = "yes24/data/yes24_ai.csv"
        df.to_csv(save_path, index=False, encoding="utf-8-sig")
        logger.info(f"총 {len(all_books)}개의 도서 정보를 수집하여 {save_path}에 저장했습니다.")
    else:
        logger.warning("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    scrape_yes24_books()
