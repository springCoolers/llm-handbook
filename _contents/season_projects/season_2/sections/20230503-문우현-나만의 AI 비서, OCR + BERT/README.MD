# 나만의 AI 비서

---

## 챗봇 시장

![1.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/12a03d61-2475-49c3-8c80-eb0231a3c5b3/1.png)

- 고객의 편리성과 회사의 경제성으로 인해 매년 전세계 챗봇 시장규모가 증가하는 추세
- precedenceresearch.com에 따르면 2023년 10억 달러(한화 약 1조 3천억원)에서 2032년 49억 달러(한화 약 6조 6천억원)로 증가할 것으로 전망
- 이는 향후 10여년동안 5배이상, 연평균 19.29%씩 증가하는 시장으로 매우 전망이 밝고 발전 가능성도 무궁무진한 분야

---

## 현재 Chat-bot의 문제점

![2.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/b8a7a75a-4bcc-47b2-b207-ad85867feaa8/2.png)

- 룰베이스에 의한 기계적인 답변
- 회사들마다 통합되지 않는 다른 모델들을 제공
- Chat-gpt와 같이 성능좋은 거대 언어모델도 답변만 할뿐 직접적으로 업무를 위임하여 수행하지 않음
- 사람 마다 개인화된 모델이 아님

---

## 내가 만들 Chat-bot 비서

- 보다 자연스러운 답변
- 하나의 문제(회사)에만 적용되는 모델이 아닌 범용적으로 사용 가능한 모델
- 어시스턴스로써의 조언 뿐만 아니라 일을 위임해서 대신 하는 비서 역할을 수행
- 대화를 통해 사용자의 성향을 파악하여 지속적으로 학습(강화학습)

---

## 타임 테이블

- 문서 Q&A 및 요약 모델 학습
- Transformer 모델의 성능 향상
- 사용자의 명령에 일을 수행하는 모델 학습

---

## Transformer

### Transformer 모델

![1.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/f26edbb5-1d40-4917-b408-8343a24a85da/1.png)

- Transformer 모델은 Attention만으로 이루어진 encoder-decoder 구조의 seqence to seqence 모델
- Transformer는 현재 최고의 성능(SOTA)을 자랑하는 모델 구조로서 자연어처리(NLP)뿐만 아니라 컴퓨터 비전(CV)에서도 최고 성능을 달성
- Transformer는 자연어처리 분야에서 GPT나 BERT와 같은 언어모델을 구성하는 기본적인 모델 구조 (Transformer를 여러층 쌓아 언어모델을 만듦.)

### Transformer 성능 개선 필요성

![3.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/349836b8-9327-43cc-a693-11bdda103341/3.png)

- 현재 언어모델의 파라미터수를 증가하면 성능이 좋아진다는 이론은 자연어 처리 분야에서 정설로 받아들여지고 있음
- 때문에 허깅페이스에서 공개한 그래프와 같이 최신 모델일수록 모델의 성능을 높이기 위해 모델의 크기가 기하급수적으로 증가
- 그러나 이렇게 모델의 크기를 늘려 성능을 향상시키는 방식은 기술적, 비용적 한계가 있음 (무작정 모델의 크기만을 늘릴수는 없기 때문에)
- 때문에 최근 언어모델의 가장 기본요소인 Transformer의 성능을 개선해야 한다는 목소리가 높아짐

## Next Generation Transformer

### Layer Normalization

![4.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/bf0ab6f8-6b41-49f9-a6a3-6939fd52cfdd/4.png)

- Layer Normalization란 모델 입력 인스턴스(x)별로 평균을 빼주고 표준편차를 나누어주어 정규화를 수행하는 방법
- Layer Normalization을 하게되면 모델의 입력데이터값이 정규화되어 안정해짐. 때문에 오른쪽 그래프와 같이 모델의 학습이 더욱 쉽게됨.
- Layer Normalization 공식에서 x는 입력 인스턴스, E(x)는 인스턴스의 평균, V(x)는 인스턴스의 분산, gamma와 beta는 학습 웨이트를, epsilon은 분모를 ‘0’으로 만들지 않기위한 작은 상수를 나타냄.

![5.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/8f163f68-14ed-4004-bfa6-e1b8db267c95/5.png)

- Transformer의 input 데이터의 분포가 불안정한 것을 파악하여, 이 부분을 lay normalization 함
- Input 지점에서 input embedding과 positional encoding 이렇게 두종류의 데이터가 만나므로 각각을 normalization 해주고 최종적으로 두 데이터를 합쳐 다시한번 normalization을 진행

![10.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/cc2afc98-0586-4ab3-b8e6-acb4e4f6b833/10.png)

- 다음 결과와 같이 layer normalization을 input 부분에 추가했을때 평균적으로 bleu 점수가 227.60%가 좋아짐

### Residual Connection

![6.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/8bc2e77f-bcb3-48d0-912d-03996a1d73b8/6.png)

- 최근 거대 모델들의 등장으로 모델 layer의 깊이가 점점 깊어짐. 그러나 layer의 수가 무작정 증가하면 모델의 gradient가 ‘0’으로 수렴하거나 ‘무한대’로 발산할 수 있어 오히려 성능이 저하됨. (Gradient Vanishing과 Exploding문제 때문에.)
- 이러한 문제점을 해결하고자 ‘Residual Connection’방법론이 등장.
- ‘Residual Connection’은 input값 ‘x’를 output값 ‘F(x)’에 더해주어 모델의 gradien값을 일정수준 유지해주어 모델의 성능을 향상

![9.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/d5f10ce1-a218-4a01-a468-a709b7ac26e3/9.png)

- 기존 residual connection 방식에서 “가중치를 두어 합하면 어떨까?”라는 궁금증에서 시작
- 가중치를 1에서 점점 높이자 Transformer의 성능 역시 점점 높아지다가 최고점을 찍고 다시 성능이 저하됨
- 다음 결과와 같이 평균적으로 bleu 점수가 기본 Transformer 모델에 비해 최대 159.76%가 좋아졌음

### Positional Encoding

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ffe7db8c-eecf-4090-93df-10108a26562c/Untitled.png)

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/41e020ad-7769-44d1-88a2-2bd704f2b44b/Untitled.png)

- Transformer가 RNN 시계열의 모델보다 성능이 좋은 이유는 데이터를 병렬처리하므로써 GPU사용효율을 극대화 시켰기 때문
- 자연어 데이터는 본래 시계열적 특성을 지니고 있으나 이를 병렬처리 할 시 시계열적 특성이 무시어되어 데이터의 순서를 알 수 없게 됨
- 때문에 병렬처리시에도 데이터의 순서를 알 수 있게 ‘Postional Encoding’이라는 기법이 발명
- ‘Postional Encoding’은 sin, cos의 삼각함수를 이용한 해당 단어의 위치정보를 나타냄

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ed546dba-202e-485c-bc62-b07f76e3141d/Untitled.png)

- Positional Encoding을 시각화 하면 위 그래프와 같은 모습이 됨. x축은 임베딩 벡터의 크기를, y축은 단어의 위치를 나타냄
- 보다시피 단어의 위치가 다르더라도 임베딩 벡터의 상당히 많은 부분이 동일하거나 유사하여 비 효율적

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/82ce1748-9754-4b5a-b6f4-7d6ea4b90d32/Untitled.png)

- 기존 삼각함수를 이용한 positional encoding 의 비효율적인 문제를 해결하기 위해 강화학습을 이용해 새로운 positional encoding 설계
- 강화학습 알고리즘은 최근 가장 성능이 좋다고 알려진 ＇SAC＇를 사용했으며, 거리가 가까운 단어들의 positional encoding은 서로 유사도가 높게, 거리가 먼 단어들의 positional encoding은 서로 유사도가 낮게 하기위한 강화학습 리워드를 설정
- 결과적으로 위와 같은 분포의 새로운 positional encoding 도출

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/01bbdff5-a0ab-4fae-8423-6287a69e6cf8/Untitled.png)

- 결과 새로운 positional encoding을 사용한 Transformer모델이 기존의 positional encoding을 사용한 모델보다 153.74% 성능이 향상

---

## 향후 계획

- 원래는 내가 개발한 Transformer를 이용해 GPT를 만들어 학습할 계획 이었으나, 컴퓨팅 자원의 한계로 방향 수정
- 컴퓨팅 자원이 많이 소비되는 프리 트레인이 완료된 모델을 이용
    - SKT KoGPT2
    - KakaoBrain KoGPT
- 위의 모델을 기계 독해 부분에 맞게 파인튜닝
    - Q&A 데이터셋 사용
    - KorQuAD
- 학습이 완료된 모델을 통해 원본 메뉴얼 문서에서 이용자가 찾는 답을 알려주고 이를 단계로 나눠 실행

---

## 레퍼런스 / 학습 자료

- [https://ratsgo.github.io/nlpbook/docs/language_model/tr_technics/#norm--레이어-정규화](https://ratsgo.github.io/nlpbook/docs/language_model/tr_technics/#norm--%EB%A0%88%EC%9D%B4%EC%96%B4-%EC%A0%95%EA%B7%9C%ED%99%94)
- https://korquad.github.io/
- https://github.com/SKT-AI/KoGPT2
- https://github.com/kakaobrain/kogpt
- https://arxiv.org/abs/1706.03762
- https://m.blog.naver.com/PostView.nhn?isHttpsRedirect=true&blogId=baek2sm&logNo=222176799509&categoryNo=99&proxyReferer=



# 나만의 AI 비서 만들기 [기말발표: BERTOCR and 법원판결예측]

작성자: 우현 문
작성 팀: S6_깃헙에 NLP  잔디심기 2
기술 분류: 자연어처리
상태: Not started
최종 편집 일시: 2023년 6월 28일 오후 9:26

# 나만의 AI 비서

---

## 원래 계획과 변경사항

- BERT와 GPT같은 언어모델들을 파인튜닝하여 메뉴얼을 이해하고 이를 통해 요약, 사람대신 업무를 수행해주는 고급 업무 자동화 NLP 모델을 만들 계획이었음.
- 그러나 나는 언어모델들을 세부적으로 분석및 연구하여 모델의 성능을 향상하는 방법은 알지만, 아직 데이터를 직접 정제하고 모델을 불러와서 직접 파인튜닝해본 경험이 없어 어려움에 봉착함.
- 때문에 나만의 AI 비서 프로젝트는 중장기적인 프로젝트로 정하고, 이번 프로젝트는 나만의 AI 비서 프로젝트를 보다 잘 진행할 수 있도록 하기위한 디딤돌 프로젝트로 선정함.
- 이번 프로젝트는 BERT와 결합된 OCR(**Optical Character Recognition**)과 DACON의 “**법원 판결 예측 AI 경진대회**”준비로 진행함.

---

# OCR

![ocr.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/ocr.png)

- OCR은 “Optical Character Recognition”의 약자로, 우리말로 하면 “광학 문자 인식”임.
- 사람이 쓰거나 기계로 인쇄한 문자의 영상을 이미지 스캐너로 획득하여 기계가 읽을 수 있는 문자로 변환하는 것.

---

## 기존 OCR의 문제점

- CV만을 이용해 문자를 인식
- 때문에 노이즈가 있는 데이터에 취약함
- 이를 해결하기위해 디노이징 기법이 사용되고 있지만 이 역시 CV에 국한된 기법임
- 이러한 문제를 해결하고자 나는 OCR에 NLP를 적용하여, 문맥으로 노이즈 데이터를 예측할 수 있는 모델을 만듦

---

## 아이디어 착안

- 우리는 길을 가다가 표지판이나 간판의 중간중간 단어가 잘 보이지 않을때 시각적인 정보 뿐만 아니라 문맥이나 상황을 고려하여 이를 유추함
- 이러한 내 경험을 바탕으로 아이디어를 구성

---

## 아이디어

![BERTOTR.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/BERTOTR.png)

- 기존의 OTR모델에 언어모델인 BERT를 추가
- 처음에 문자 데이터를 OTR모델에 입력하고 출력값을 통해 신뢰도를 계산
- 신뢰가 부족한 데이터는 그 다음 언어모델인 BERT로 입력후 다시 출력
- BERT역시 해당 출력값에 신뢰도가 포함되어있는데, 이때 신뢰도가 평균이상인 값들을 출력
- 이 출력값들을 다시 이미지로 변환하고 이 이미지를 원래 노이즈 이미지와 코사인 유사도를 이용해 유사도 비교
- 최종적으로 출력값의 BERT 신뢰도와 원래 이미지와의 유사도를 곱하여 가장 큰 값을 출력

![noise_data.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/noise_data.png)

- 예를들어 위와같은 노이즈 데이터가 있을때 처음 OCR 모델이 ‘selling’이라는 단어를 ‘age’라고 예측 했고 이 신뢰도가 0.04이고 모델러가 신뢰도 상수 k = 0.5라고 가정했다면, 이 단어는 신뢰할 수 없는 단어임.
- OCR 예측: “was voted top [age] animespecial effects DVD”
- 신뢰도가 낮은 단어 ‘age’를 [MASK] token으로 변경후 BERT 모델에 입력(“was voted top [MASK] animespecial effects DVD”)
- BERT는 앞, 뒤 문맥을 파악하여 [MASK] token을 예측: [selling=0.4, rate=0.3, gel=0.1, apple=0.1, banana=0.1]
- 이때 연산효율을 높이기 위해 평균값((0.4+0.3+0.1+0.1+0.1)/5 = 0.3)보다 작은 값은 삭제 : [selling=0.4, rate=0.3]

![cosine_similarity.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/cosine_similarity.png)

- 이 값들을 이미지로 변환한 뒤 노이즈 이미지와 코사인 유사도를 도출 : [selling=0.9, rate=0.3]
- 최종적으로 BERT 점수와 코사인유사도 점수를 곱해 가장 큰 값 도출 : argmax([selling=0.6*0.9=0.54, rate=0.5*0.3=0.15]) = selling

---

## 실험 및 결과

### 모델 및 데이터셋

- OCR 모델 : easyocr 모델 사용
- BERT 모델 : 허깅페이스 모델 사용
- 데이터셋으로 Wikipedia (780만 문장), CNN dailymail (30만 문장) 그리고 Fiction (2000 문장) 사용

[GitHub - JaidedAI/EasyOCR: Ready-to-use OCR with 80+ supported languages and all popular writing scripts including Latin, Chinese, Arabic, Devanagari, Cyrillic and etc.](https://github.com/jaidedai/easyocr)

[EasyOCR Python Tutorial with Examples - MLK - Machine Learning Knowledge](https://machinelearningknowledge.ai/easyocr-python-tutorial-with-examples/)

[](https://huggingface.co/docs/transformers/main/en/modeldoc/bert)

[Wikipedia Sentences](https://www.kaggle.com/datasets/mikeortman/wikipedia-sentences)

[GitHub - abisee/cnn-dailymail: Code to obtain the CNN / Daily Mail dataset (non-anonymized) for summarization](https://github.com/abisee/cnn-dailymail)

[Fiction stories dataset](https://www.kaggle.com/datasets/jayashree4/fiction)

### 결과

![결과1.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/%25EA%25B2%25B0%25EA%25B3%25BC1.png)

![결과2.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/%25EA%25B2%25B0%25EA%25B3%25BC2.png)

- Conventional OCR : OCR
- OCR and BERT : OCR + BERT
- BERTOCR : OCR + BERT + Cosine Similarity
- 내가 제안한 BERTOCR 모델이 평균적으로 Conventional OCR 보다 333.67% 더 좋았고, OCR and BERT 보다 3.62% 더 좋았다(유사도 비교 블럭의 유무 차이)

---

# 법원 판결 예측

---

## 게임 설명

![train.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/train.png)

![test.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/test.png)

- test dataset : first_party, second_party, facts와 first_party_winner로 구성
- first_party_winner가 1이면 first_party가 재판에서 이김, first_party_winner가 0이면 first_party가 재판에서 짐
- train dataset :  first_party, second_party와 facts로 구성
- train dataset으로 모델을 학습시켜, 학습시킨 모델로 test dataset를 잘 맞추는 사람이 승리

[월간 데이콘 법원 판결 예측 AI 경진대회](https://dacon.io/competitions/official/236112/overview/description)

---

## 방법

### 데이터 불균형 해결

![unbalance.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/unbalance.png)

- train datatset에 first_party_winner가 1인 데이터가 0인것에 비해 두배가량 많음
- 데이터셋의 불균형으로 모델이 편향적으로 학습할 수 있음
- 때문에 이 문제를 다음과 같이 해결
    - 다운샘플링 : 지금 first_party_winner = 0: 800여개, first_party_winner = 1: 1600여개 이므로 first_party_winner = 1을 랜덤으로 800여개를 추출하여 두 데이터셋 사이의 균형을 맞춤
    - 업샘플링 : 위 다음샘플링과 반대로, first_party_winner = 0 데이터의 수를 상대적으로 늘려 두 데이터셋의 균형을 맞춤
        - 예를들어 first_party: tony/ second_party: jack/ fact: tony hit jack/ first_party_winner = 0 데이터셋을 first_party: tony/ second_party: jack/ fact: jack hit tony/ first_party_winner = 1로 변환(이러면 데이터셋의 균형이 맞음)
        
         
        

### 이름 변환 및 추가

![data2.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/data2.png)

![data.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/data.png)

---

- dataset에 다양한 이름들이 등장, 때문에 모델이 누가 누구인지 학습하기가 어려움
- 때문에 first_party와 second_party 이름들을 tony와 jack으로 통일
- 약자의 경우에도 고려해서 변환
- 예를들어 Monkey Banana == MB

![data3.png](%E1%84%82%E1%85%A1%E1%84%86%E1%85%A1%E1%86%AB%E1%84%8B%E1%85%B4%20AI%20%E1%84%87%E1%85%B5%E1%84%89%E1%85%A5%20%E1%84%86%E1%85%A1%E1%86%AB%E1%84%83%E1%85%B3%E1%86%AF%E1%84%80%E1%85%B5%20%5B%E1%84%80%E1%85%B5%E1%84%86%E1%85%A1%E1%86%AF%E1%84%87%E1%85%A1%E1%86%AF%E1%84%91%E1%85%AD%20BERTOCR%20and%20%E1%84%87%20f50c6f1cc98840e29974016af11cbf07/data3.png)

- 모델이 first_party와 second_party을 더욱 알기쉽게 하기위해 facts 데이터셋 앞부분에  first_party와 second_party 이름인 tony와 jack 추가

---

## 결과

정확도 : 0.52903

## 레퍼런스 / 학습 자료

- [https://ratsgo.github.io/nlpbook/docs/language_model/tr_technics/#norm--레이어-정규화](https://ratsgo.github.io/nlpbook/docs/language_model/tr_technics/#norm--%EB%A0%88%EC%9D%B4%EC%96%B4-%EC%A0%95%EA%B7%9C%ED%99%94)
- [https://korquad.github.io/](https://korquad.github.io/)
- [https://github.com/SKT-AI/KoGPT2](https://github.com/SKT-AI/KoGPT2)
- [https://github.com/kakaobrain/kogpt](https://github.com/kakaobrain/kogpt)
- [https://arxiv.org/abs/1706.03762](https://arxiv.org/abs/1706.03762)
- [https://m.blog.naver.com/PostView.nhn?isHttpsRedirect=true&blogId=baek2sm&logNo=222176799509&categoryNo=99&proxyReferer=](https://m.blog.naver.com/PostView.nhn?isHttpsRedirect=true&blogId=baek2sm&logNo=222176799509&categoryNo=99&proxyReferer=)

---
