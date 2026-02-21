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
    logger.info("데이터 분석 시작: yes24/data/yes24_ai.csv")
    
    # 1. 데이터 로드 (quoting 옵션 추가하여 쉼표 포함 필드 대응)
    try:
        df = pd.read_csv("yes24/data/yes24_ai.csv", encoding='utf-8-sig', on_bad_lines='warn')
        logger.info(f"데이터 로드 완료. 행 수: {len(df)}, 컬럼: {df.columns.tolist()}")
    except Exception as e:
        logger.error(f"파일 로드 실패: {e}")
        return

    # 2. 데이터 전처리
    numeric_cols = ['정가', '판매가', '리뷰수', '판매지수']
    
    # 디버깅: 전처리 전 상태 확인
    for col in numeric_cols:
        if col in df.columns:
            logger.debug(f"컬럼 '{col}' 샘플: {df[col].head(3).tolist()}")

    for col in numeric_cols:
        if col in df.columns:
            # 모든 데이터를 문자열로 변환 후 정제
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('원', '').str.strip()
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 3. 시각화 수행
    
    # 3.1 판매가 분포 히스토그램
    plt.figure(figsize=(10, 6))
    df_filtered_price = df[df['판매가'] > 0]
    df_filtered_price = df_filtered_price[df_filtered_price['판매가'] <= 100000]
    plt.hist(df_filtered_price['판매가'], bins=30, color='skyblue', edgecolor='black', alpha=0.7)
    plt.title("AI 도서 판매가 분포 (10만원 이하)", fontsize=15)
    plt.xlabel("가격(원)")
    plt.ylabel("도서 수")
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.savefig("yes24/data/charts/price_dist.png")
    plt.close()

    # 3.2 상위 10개 출판사 바 차트
    plt.figure(figsize=(12, 6))
    top_publishers = df['출판사'].value_counts().head(10)
    top_publishers.plot(kind='bar', color='#ff9999', edgecolor='black')
    plt.title("상위 10개 출판사 도서 등록 현황", fontsize=15)
    plt.ylabel("도서 수")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("yes24/data/charts/top_publishers.png")
    plt.close()

    # 3.3 판매지수 상위 10개 도서 (가로 바 차트)
    plt.figure(figsize=(12, 8))
    top_sales_books = df.sort_values(by='판매지수', ascending=False).head(10)
    top_sales_books['단축제목'] = top_sales_books['제목'].apply(lambda x: (str(x)[:20] + '...') if len(str(x)) > 20 else str(x))
    sns.barplot(x='판매지수', y='단축제목', data=top_sales_books, hue='단축제목', palette='viridis', legend=False)
    plt.title("판매지수 Top 10 도서", fontsize=15)
    plt.xlabel("판매지수")
    plt.ylabel("도서명")
    plt.tight_layout()
    plt.savefig("yes24/data/charts/top_sales_books.png")
    plt.close()

    # 3.4 판매지수와 리뷰수의 상관관계 산점도
    plt.figure(figsize=(10, 6))
    plt.scatter(df['판매지수'], df['리뷰수'], alpha=0.5, color='green', s=50)
    plt.title("판매지수와 리뷰수의 상관관계", fontsize=15)
    plt.xlabel("판매지수")
    plt.ylabel("리뷰수")
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.savefig("yes24/data/charts/sales_vs_reviews.png")
    plt.close()

    # 3.5 제목 키워드 워드클라우드
    titles_text = " ".join(df['제목'].dropna().astype(str))
    stopwords = ['위한', '활용법', '만들기', '함께하는', '시대', '방법', '완성하는', '가이드', '입문', '실전', '끝내는', '하루', '만에']
    for word in stopwords:
        titles_text = titles_text.replace(word, '')
        
    font_path = "C:/Windows/Fonts/malgun.ttf"
    if not os.path.exists(font_path):
        font_path = "C:/Windows/Fonts/malgunbd.ttf"
        
    wordcloud = WordCloud(
        font_path=font_path,
        background_color='white',
        width=1000, height=600,
        max_words=100
    ).generate(titles_text)
    
    plt.figure(figsize=(15, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title("AI 도서 제목 핵심 키워드", fontsize=20)
    plt.savefig("yes24/data/charts/wordcloud.png")
    plt.close()

    # 4. 결과 요약 출력
    print("\n[Analysis Summary]")
    print(f"Total Books: {len(df)}")
    print(f"Average Price: {df['판매가'].mean():,.0f} KRW")
    if not top_publishers.empty:
        print(f"Top Publisher: {top_publishers.index[0]} ({top_publishers.iloc[0]} books)")
    print(f"Max Sales Index: {df['판매지수'].max():,.0f}")
    
    # 최고 판매 도서 확인
    if not df.empty:
        top_book = df.loc[df['판매지수'].idxmax()]
        print(f"Top Selling Book: {top_book['제목']} (Index: {top_book['판매지수']:,.0f})")

if __name__ == "__main__":
    perform_eda()
