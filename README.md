# 국내 학술 논문 기반 생성형 AI 연구 동향 분석 (2021–2025)

DBpia 학술 논문 메타데이터(2021-2025)를 기반으로 생성형 AI를 비롯한 머신러닝, 딥러닝 활용 논문들을 분석하였다. 다만 생성형 AI는 비교적 최근에 본격화된 연구 분야로, 제한된 기간의 데이터만을 단독으로 분석할 경우 연구 주제의 구조적 특성을 충분히 설명하는 데 한계가 있다고 판단하였다.

이에 분석에서는 생성형 AI를 보다 넓은 AI 연구 맥락에서 이해하기 위해 생성형 AI, 딥러닝, 전통적 머신러닝의 세 범주로 분석 대상을 확장하였다.

분석 방법으로는 각 범주에 대해 TF-IDF 및 BERTopic을 적용하여 주요 키워드와 토픽 구성을 도출하고, 범주 간 연구 주제 구조 및 변화 양상을 비교 분석하였다.

<br>

# 실행 환경
> Platform: Google Colab<p>
> CPU: Intel Xeon (2 cores)<p>
> RAM: 12.7 GB<p>
> GPU: Tesla T4 (권장)<p>

<br>

# 분석 흐름

## Step 1: 논문 복구
- 원본 데이터: 62,199건
- 복구 성공: 61,990건 (구조적으로 복구 가능한 레코드)
- 식별 불가: 209건
- 자세한 내용은 `paper-classification` 브랜치 참조

## Step 2: 텍스트 전처리 및 토큰화

### 2-1. 불용어 처리
- NLTK stopwords + 사용자 지정(STOP_KR, STOP_EN)

### 2-2. 토큰화

**국문 토큰화 (ko_tokens)**
- 대상 필드: `NODE_TTLE`, `ABST_KR`, `KYWD` (국문 텍스트 및 영문 혼합 키워드)
- 형태소 분석기: Kiwi (https://github.com/bab2min/Kiwi)
- 처리 과정:
  1. 토큰화 전 필요한 앵커 집합 및 단어들을 특정 표기로 통일
  2. Kiwi 형태소 토큰 중 명사 계열(NN*), 외래어(SL), 접두사(XPN) 품사에 대해 공백 없이 원문 텍스트에서 붙은 형태인 경우 의미 보존을 위해 합침
     - 처리: 명사+명사 / 접두사+명사 / 명사+명사접미사
  3. 길이 1 이하 및 STOP_KR에 속한 경우 제거 & 정규식 필터 적용

**영문 토큰화 (en_tokens)**
- 대상 필드: `NODE_TTLE_EN`, `ABST_EN`, `KYWD` (영문 텍스트 키워드)
- NLP 라이브러리: NLTK
- 처리 과정:
  1. 전부 소문자화(lower())
  2. 전처리는 normalize_text_pre_tokenize, NLTK 토큰화는 word_tokenize로 진행, 품사 태깅은 pos_tag으로 처리
  3. 문자 정리 및 불용어 제거
  4. 약어 및 복수형 처리(예: llms → llm) & 정규식 필터 적용

### 2-3. 바이그램 마이닝
- `mine_bigrams_pmi`로 자주 같이 나오는 단어쌍을 검색해서 병합 처리
- PMI 기반: log2(P(a,b) / (P(a) * P(b)))

### 2-4. 키워드 우선 병합
- `merge_kw_body_tokens(본문토큰, 키워드phrase리스트)`로 키워드 먼저 삽입 후 본문 토큰 중복 제거 추가
  1. `split_kywd_field`로 전부 ','로 자른 후 `normalize_kw_piece` 정리
  2. `split_kywd_item_ko_en`으로 국문/영문 분리(괄호 처리 포함) & 약어 처리

### 2-5. 단일 토큰 문서 필터링
- token_len == 1인 문서들 중 `drop_solo_tokens` 목록(예: 머리말/학회소식류 등)에 속하는 경우 대다수 의미 분석 불가능하니 3번 이상 나온 논문 제거

### 2-6. 최종 토큰 데이터 저장
- 파일명: `df_tokens.parquet`
- 컬럼: `NODE_ID`, `PBSH`, `NODE_CLSS_02`, `NODE_TTLE`, `NODE_TTLE_EN`, `ABST_KR`, `ABST_EN`, `KYWD`, `ko_text`, `en_text`, `ko_tokens`, `en_tokens`, `merged_tokens_dedup`

## Step 3: TF-IDF 및 BERTopic

코드에 주석 및 설명이 되어있어 간단히 설명. BERTopic 내 시각화를 사용했으나 해당 방식은 GitHub의 렌더링 한계로 업로드할 수 없어 BERTopic의 삭제 부분 위주로 작성함.

### 3-1. BERTopic 파이프라인
- 문서 임베딩 → UMAP → HDBSCAN → Vectorizer

### 3-2. 임베딩 모델
- `paraphrase-multilingual-MiniLM-L12-v2`

### 3-3. 하이퍼파라미터 튜닝
- 토픽 수, 단일 토픽 쏠림, outlier(-1) 영향을 통제하기 위해 UMAP 및 HDBSCAN, Vectorizer 하이퍼파라미터를 명시적으로 설정
- 단계적으로 조정하며 결과를 반복 비교

### 3-4. 분석 결과
- 렌더링 불가해서 첨부되지 못한 산출물 캡처는 아래 주요 분석 결과 요약과 함께 첨부

<br>

---

<br>

# BERTopic 주요 분석 결과 요약
## 생성형 AI
<table>
  <tr>
    <th>토픽 분포</th>
    <th>토픽 계층 확인</th>
    <th>대표 키워드</th>
    <th>연도별 토픽 비중 변화</th>
    <th>2021-2022 / 2023-2025<br>토픽 비중 변화</th>
  </tr>
  <tr>
    <td><img width="589" height="602" alt="image" src="https://github.com/user-attachments/assets/d5e7e2f2-20c2-4add-be91-4168eeffa3ea" /></td>
    <td><img width="920" height="262" alt="image" src="https://github.com/user-attachments/assets/ccabc0b1-0d3a-4476-b771-b329f4d3e112" /></td>
    <td><img width="924" height="450" alt="image" src="https://github.com/user-attachments/assets/a794f11f-fccd-44d5-80af-cab557fdc42f" /></td>
    <td><img width="918" height="448" alt="image" src="https://github.com/user-attachments/assets/69ee012a-2fec-48ab-8c4d-6dc77e605634" /></td>
    <td><img width="400" height="240" alt="image" src="https://github.com/user-attachments/assets/ff8093bc-7550-4c62-9885-c3f2378e2b70" /></td>
  </tr>
</table>

- 창작, 교육, 미디어 등 활용 중심 토픽 비중 증가
- 초기에는 일반적 응용·기술 중심 연구가 주를 이루었으나, 이후 활용 분야별로 연구 주제가 세분화되는 경향이 나타남

<br>

## 전통ML
<table>
  <tr>
    <th>전통ML 바 차트 (2021-2022)</th>
    <th>전통ML 바 차트 (2023-2025)</th>
  </tr>
  <tr>
    <td><img width="951" height="417" alt="Screenshot 2026-02-02 at 12 21 22 pm" src="https://github.com/user-attachments/assets/4a338f77-ed8c-40a4-a464-6f784c9f22e9" />
    <td><img width="956" height="418" alt="Screenshot 2026-02-02 at 12 21 56 pm" src="https://github.com/user-attachments/assets/8378f388-99b4-4a6e-b5f0-151107ed7357" /></td>

  </tr>
</table>


<table>
  <tr>
    <th>전통ML 토픽 분포<br>(2021-2022)</th>
    <th>전통ML 토픽 분포<br>(2023-2025)</th>
    <th>전통ML 토픽 계층 확인<br>(2021-2022)</th>
    <th>전통ML 토픽 계층 확인<br>(2023-2025)</th>
  </tr>
  <tr>
    <td><img width="797" height="797" alt="image" src="https://github.com/user-attachments/assets/dc3951ef-a6d0-437f-a802-e1def0b98ece" />
    <td><img width="797" height="797" alt="image" src="https://github.com/user-attachments/assets/f4dfcf24-37de-4aa3-bf92-d2af1541c3e9" />
    <td><img width="1173" height="542" alt="image" src="https://github.com/user-attachments/assets/45955c9a-a867-4ed7-979f-62566d6dccc1" />
    <td><img width="1171" height="713" alt="image" src="https://github.com/user-attachments/assets/866ef774-c8f6-41f3-b077-8fd7af776c71" />
  </tr>
</table>

<br>

## 딥러닝
<table>
  <tr>
    <th>딥러닝 바 차트 (2021-2022)</th>
    <th>딥러닝 바 차트 (2023-2025)</th>
  </tr>
  <tr>
    <td><img width="931" height="436" alt="Screenshot 2026-02-02 at 12 31 51 pm" src="https://github.com/user-attachments/assets/ca943633-0b82-469c-82b0-d9d7c2b2fa04" />
    <td><img width="957" height="427" alt="Screenshot 2026-02-02 at 12 32 22 pm" src="https://github.com/user-attachments/assets/cdc9060d-f522-471c-9674-34ada7941f1b" />
  </tr>
</table>

<table>
  <tr>
    <th>딥러닝 토픽 분포<br>(2021-2022)</th>
    <th>딥러닝 토픽 분포<br>(2023-2025)</th>
    <th>딥러닝 토픽 계층 확인<br>(2021-2022)</th>
    <th>딥러닝 토픽 계층 확인<br>(2023-2025)</th>
  </tr>
  <tr>
    <td><img width="797" height="797" alt="image" src="https://github.com/user-attachments/assets/2f5dd76e-da76-441e-8e5a-a8bcd5a5c96a" />
    <td><img width="797" height="797" alt="image" src="https://github.com/user-attachments/assets/a3923b9e-fa31-415f-9f72-e25c3265240d" />
    <td><img width="1173" height="542" alt="image" src="https://github.com/user-attachments/assets/7dfa3233-b91a-4210-ad5c-31c11315a93a" />
    <td><img width="1171" height="713" alt="image" src="https://github.com/user-attachments/assets/4e6582aa-120f-43dd-a541-3e0111ad4b04" />
  </tr>
</table>

- 보안(Security) 관련 연구의 전반적 확대
- 의료·헬스케어 분야는 전통적 머신러닝(설문·정형 데이터)과 딥러닝(영상 데이터) 모두에서 상위 토픽으로 유지
- 로봇 제어, 결함 탐지, 에너지 등 산업 AI 응용 연구 증가


