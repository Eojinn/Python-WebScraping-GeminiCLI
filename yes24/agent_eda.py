import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from wordcloud import WordCloud
import os
from loguru import logger

# 디렉토리 설정
os.makedirs("yes24/data/charts", exist_ok=True)

def perform_eda():
    logger.info("EDA 시작: yes24/data/yes24_ai.csv")
    
    # 데이터 로드 (헤더가 한글인 경우와 영문인 경우 모두 대응)
    try:
        df = pd.read_csv("yes24/data/yes24_ai.csv")
    except Exception as e:
        logger.error(f"파일 로드 실패: {e}")
        return

    # 컬럼명 매핑 (영문 -> 한글 변환 또는 유지)
    column_mapping = {
        'title': '제목', 'author': '저자', 'publisher': '출판사', 
        'sale_price': '판매가', 'original_price': '정가', 
        'sales_index': '판매지수', 'review_count': '리뷰수', 'rating': '평점'
    }
    df = df.rename(columns=column_mapping)

    # 1. 수치형 데이터 정제 (콤마 제거 등)
    for col in ['판매가', '정가', '판매지수', '리뷰수']:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = df[col].str.replace(',', '').astype(float)

    # 2. 가격 분포 시각화
    plt.figure(figsize=(10, 6))
    plt.hist(df['판매가'].dropna(), bins=20, color='skyblue', edgecolor='black')
    plt.title("도서 판매가 분포")
    plt.xlabel("가격(원)")
    plt.ylabel("도서 수")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig("yes24/data/charts/price_dist.png")
    plt.close()

    # 3. 출판사별 도서 수 (상위 10개)
    plt.figure(figsize=(12, 6))
    top_publishers = df['출판사'].value_counts().head(10)
    top_publishers.plot(kind='bar', color='salmon')
    plt.title("상위 10개 출판사별 도서 등록 수")
    plt.xticks(rotation=45)
    plt.ylabel("도서 수")
    plt.savefig("yes24/data/charts/top_publishers.png")
    plt.close()

    # 4. 판매지수 vs 리뷰수 상관관계
    plt.figure(figsize=(10, 6))
    plt.scatter(df['판매지수'], df['리뷰수'], alpha=0.5, color='green')
    plt.title("판매지수와 리뷰수의 상관관계")
    plt.xlabel("판매지수")
    plt.ylabel("리뷰수")
    plt.savefig("yes24/data/charts/sales_vs_reviews.png")
    plt.close()

    # 5. 제목 키워드 워드클라우드
    titles = " ".join(df['제목'].dropna().astype(str))
    wordcloud = WordCloud(
        font_path='Malgun Gothic', # Windows 기준
        background_color='white',
        width=800, height=400
    ).generate(titles)
    
    plt.figure(figsize=(15, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("도서 제목 키워드 워드클라우드")
    plt.savefig("yes24/data/charts/wordcloud.png")
    plt.close()

    # 통계 요약 정보 리턴
    summary = {
        "total_count": len(df),
        "mean_price": df['판매가'].mean(),
        "max_sales_book": df.loc[df['판매지수'].idxmax(), '제목'] if '판매지수' in df.columns else "N/A",
        "top_publisher": top_publishers.index[0]
    }
    return summary

if __name__ == "__main__":
    summary = perform_eda()
    print(summary)
