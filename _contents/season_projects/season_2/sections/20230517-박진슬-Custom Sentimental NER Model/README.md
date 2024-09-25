# 박진슬 - Custom Sentimental NER Model


## 프로젝트 기획

- 목표 : 개인이 주기적으로 작성하는 글 속에 존재하는 주된 감정(정서) 와 단어 추출

### 1. 데이터셋

- 개인 에세이 글
- 한국어 말뭉치
    
    https://corpus.korean.go.kr/request/corpusRegist.do
    
    ![스크린샷 2023-04-12 20.27.01.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/e2e32b8a-4a6c-4f04-b72b-83f7f25aad3e/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2023-04-12_20.27.01.png)
    
    https://www.dacon.io/competitions/official/236037/data
    
    https://aida.kisti.re.kr/data/8d0fd6f4-4bf9-47ae-bd71-7d41f01ad9a6
    
- 정신의학칼럼 - 크롤링
    
    http://www.psychiatricnews.net/
    
    ![스크린샷 2023-04-12 19.50.00.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/53f33c3f-8437-4b20-b6cd-3c38d2bf2969/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2023-04-12_19.50.00.png)
    

### 2. 활용방안

- 개인의 글을 넣었을 때, 그 사람의 글과 정서에 맞는 단어를 추출
- 새로운 글을 작성했을 때, 엔티티태깅된 결과를 보여줌

+) 실제로 그 글, 단어를 쓸 때 그 감정을 느꼈는지 인터뷰 / streamlit 을 통한 manual entity tagging 을 통해 정확도 개선 시도

### 3. 모델 아키텍쳐

- MultinomialNB : 다변량 범주형 나이브 베이즈 분류기
    - 개인이 작성한 글을 넣고 감정을 분류하기 위해 사용
- LIMA : Local Interpretable Model Agnostic Explanation, 모델에 상관하지 않고 각 요소의 영향력 설명하는 라이브러리
    - 분류에 도움이 된 주요 키워드 확보를 하기 위해 사용
    - 단어 임베딩 값으로 주요 정서 단어와 유사한 상위 top100개 추출(?)
    - 각 단어별 엔티티 부여
        - [회사, 퇴근, 야근] - [짜증, 짜증, 짜증]
- bi-LSTM + CRF : 양방향 LSTM + (bilou등의) 조건부 엔티티
    - 정의된 단어리스트를 활용하여, 문장 속 특정 단어의 엔티티를 달아주기 위해 사용
    - 학습에 충분한 수준의 실제 개인의 글을 수집할 수 있는지 확인 필요

### 4. 추가 리서치 해볼만 한 것들

- ABSA - 이전에 용선님 발표해주신 내용 듣고 알게되었습니다!
- LLM 활용 - GPT3 무료버전 사용을 목표로!

4-1. 유사 주제로 진행한 부분

- https://github.com/vermashivam679/YouTube_comments_NLP
- https://www.dacon.io/competitions/official/236037/data
- https://aida.kisti.re.kr/data/8d0fd6f4-4bf9-47ae-bd71-7d41f01ad9a6

4-2. 앞선 서비스 

- gpt를 사용하여 심리상담 서비스를 만든 회사 : Koko
    
    https://www.loom.com/share/d9b5a26c644640ba95bb413147e41766
    

- 심리 상담 기법 중 CBT를 활용하는 방법도 고민
    
    http://www.cbt.or.kr/content/info/info.jsp
    
    https://www.sciencedirect.com/science/article/pii/S1877050922014521
=======
프로젝트 기획

목표 : 개인이 주기적으로 작성하는 글 속에 존재하는 주된 감정(정서) 와 단어 추출

## 1. 데이터셋

- 개인 에세이 글
- 한국어 말뭉치
  - https://corpus.korean.go.kr/request/corpusRegist.do
  - https://www.dacon.io/competitions/official/236037/data
  - https://aida.kisti.re.kr/data/8d0fd6f4-4bf9-47ae-bd71-7d41f01ad9a6
- 정신의학칼럼 - 크롤링
  - http://www.psychiatricnews.net/


## 2. 활용방안
  - 개인의 글을 넣었을 때, 그 사람의 글과 정서에 맞는 단어를 추출
  - 새로운 글을 작성했을 때, 엔티티태깅된 결과를 보여줌
  - 실제 글,단어를 쓸 때 그 감정을 느꼈는지 인터뷰 / streamlit 을 통한 manual entity tagging 을 통해 정확도 개선 시도

## 3. 모델 아키텍쳐

  - MultinomialNB : 다변량 범주형 나이브 베이즈 분류기
    개인이 작성한 글을 넣고 감정을 분류하기 위해 사용
  - LIMA : Local Interpretable Model Agnostic Explanation, 모델에 상관하지 않고 각 요소의 영향력 설명하는 라이브러리
    - 분류에 도움이 된 주요 키워드 확보를 하기 위해 사용
    - 단어 임베딩 값으로 주요 정서 단어와 유사한 상위 top100개 추출(?)
  
  - 각 단어별 엔티티 부여
    [회사, 퇴근, 야근] - [짜증, 짜증, 짜증]
  - bi-LSTM + CRF : 양방향 LSTM + (bilou등의) 조건부 엔티티
    정의된 단어리스트를 활용하여, 문장 속 특정 단어의 엔티티를 달아주기 위해 사용
    학습에 충분한 수준의 실제 개인의 글을 수집할 수 있는지 확인 필요

## 4. 추가 리서치 해볼만 한 것들

  - ABSA 
  - LLM 활용 - GPT3 무료버전 사용을 목표로!

### 4-1. 유사 주제로 진행한 부분

  - https://github.com/vermashivam679/YouTube_comments_NLP
  - https://www.dacon.io/competitions/official/236037/data
  - https://aida.kisti.re.kr/data/8d0fd6f4-4bf9-47ae-bd71-7d41f01ad9a6

### 4-2. 앞선 서비스

  - gpt를 사용하여 심리상담 서비스를 만든 회사 : Koko
    - https://www.loom.com/share/d9b5a26c644640ba95bb413147e41766

  - 심리 상담 기법 중 CBT를 활용하는 방법도 고민
    - http://www.cbt.or.kr/content/info/info.jsp
    - https://www.sciencedirect.com/science/article/pii/S1877050922014521
