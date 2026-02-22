import os
import requests
import pandas as pd
from loguru import logger
import time

# 로거 설정
logger.add("starbucks_stores/log/starbucks_scraper_{time}.log", rotation="500 MB")

def scrape_starbucks_stores():
    """전국 스타벅스 매장 정보를 수집하여 CSV로 저장합니다."""
    
    url = "https://www.starbucks.co.kr/store/getStore.do?r=X2D6LNU8AB"
    
    headers = {
        "host": "www.starbucks.co.kr",
        "origin": "https://www.starbucks.co.kr",
        "referer": "https://www.starbucks.co.kr/store/store_map.do",
        "sec-ch-ua": '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest"
    }
    
    all_stores = []
    
    # p_sido_cd 01 (서울) 부터 17 (세종) 까지 반복
    for i in range(1, 18):
        sido_cd = f"{i:02d}"
        logger.info(f"p_sido_cd={sido_cd} 매장 정보 수집 중...")
        
        payload = {
            "in_biz_cds": "0",
            "in_scodes": "0",
            "ins_lat": "37.56682",
            "ins_lng": "126.97865",
            "search_text": "",
            "p_sido_cd": sido_cd,
            "p_gugun_cd": "",
            "isError": "true",
            "in_distance": "0",
            "in_biz_cd": "",
            "iend": "1000",
            "searchType": "C",
            "set_date": "",
            "rndCod": "9QQ7ILZT2H",
            "all_store": "0",
            "T03": "0",
            "T01": "0",
            "T27": "0",
            "T12": "0",
            "T09": "0",
            "T30": "0",
            "T05": "0",
            "T22": "0",
            "T21": "0",
            "T36": "0",
            "T43": "0",
            "Z9999": "0",
            "T64": "0",
            "T66": "0",
            "P02": "0",
            "P10": "0",
            "P50": "0",
            "P20": "0",
            "P60": "0",
            "P30": "0",
            "P70": "0",
            "P40": "0",
            "P80": "0",
            "whcroad_yn": "0",
            "P90": "0",
            "P01": "0",
            "new_bool": "0"
        }
        
        try:
            response = requests.post(url, headers=headers, data=payload)
            response.raise_for_status()
            
            data = response.json()
            stores = data.get("list", [])
            
            if stores:
                logger.info(f"p_sido_cd={sido_cd}에서 {len(stores)}개의 매장을 찾았습니다.")
                all_stores.extend(stores)
            else:
                logger.warning(f"p_sido_cd={sido_cd}에서 매장 정보를 찾을 수 없습니다.")
                
            # 서버 부하 방지를 위해 짧은 대기 시간 추가
            time.sleep(0.5)
            
        except Exception as e:
            logger.error(f"p_sido_cd={sido_cd} 수집 중 오류 발생: {e}")
            
    if all_stores:
        df = pd.DataFrame(all_stores)
        
        # 저장 경로 확인 및 생성
        data_dir = "starbucks_stores/data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"디렉토리 생성: {data_dir}")
            
        file_path = os.path.join(data_dir, "starbucks_ai.csv")
        df.to_csv(file_path, index=False, encoding="utf-8-sig")
        logger.info(f"총 {len(all_stores)}개의 매장 정보를 {file_path}에 저장 완료하였습니다.")
    else:
        logger.error("수집된 매장 정보가 없습니다.")

if __name__ == "__main__":
    scrape_starbucks_stores()
