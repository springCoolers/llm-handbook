# NCWD - 삽질하는 중기

# 이번주 한 일

- Dataset - Crypto News Aggregator라는걸 활용해서 모아봤습니다.
- 2021-2023년 사이 뉴스기사 2만건: headline과 text의 첫 줄
- NER Pipeline 모았고
- TF-IDF 한번 써봄

## Dataset의 문제

- 내가 생각했던 단어들이 너무 희소한 빈도로 나옴.  (TF-IDF가 의미없어짐)
    - 인명, 기관명, 뭐 코인 이름은 나옴.
    - “무슨 코인이 어디에 상장되었다” / “누가 얼마라고 가격을 예측했다”
- 그런데 Headline에는 생각보다 tech 개념들이 안 나옴.
- [ ]  아예 데이터부터 새로 찾자…

## NER + OOV 접근의 문제점

파인튜닝 안한 LLM의 토크나이저에 넣고, OOV로 걸러내야겠다고 생각함

- Shibainu - 이런건 잡아내겠지

고유명사는 잡아낼 수 있는듯

- Gary Gensler / Justing Hong → 이건 아마도 학습됨

아래 케이스들을 못걸러냄 안됨

1. WorldCoin, stablecoin →  stable/coin 으로 subword들이 이미 있음 → OOV가 안나옴 
2. account abstraction, NFT Bound account → 기존 단어들의 조합으로 새로 됨
3. sequencer, zero knowledge → 기존에 존재하던 개념이지만 새롭게 주목받는 단어
4. soul bound token / soulbound token → 표기가 정착되지 않았음.
5. SBT → 줄임말은 어려움

<aside>
💡 망했다

</aside>

# 새로운 접근

1. 문서 요약 task로 바꿈 → 요약에서 key words extraction이 되지 않을까? 
    1. GPT에게 시킨다……….  
2. keyword를 bingchat에 던져서, 단어의 뜻 + trending + 언제 만들어졌는 여부를 return하게 만든다.  
3. 블록체인 뉴스로 경량화 LLM에 파인튜닝을 시켜야겠음 

## 도와줘요 챗GPT

아래와 같은 프롬프트를 입력했습니다. 
![image](https://github.com/springcoolers/weekly-presentation/assets/49356933/ddb969a3-5c33-4c00-b17b-79b30f426033)

이후 텍스트를 입력했습니다. 
![image](https://github.com/springcoolers/weekly-presentation/assets/49356933/4f9857cb-92f1-4d2e-8ade-b39b0766a52c)

아래와 같은 답변이 나왔구요
![image](https://github.com/springcoolers/weekly-presentation/assets/49356933/3e7fb33d-5246-48c6-b910-4e235b821f33)

- 그냥 저 목록을 그대로 bingchat / google trend같은데에 던지면, 생성일자와 뜻이 나올 듯
- 그 데이터로 glossary를 구축한다.

## Bingchat에 던지기

그다지 결과가 좋지 않다. 데이터가 없는걸까? 
![image](https://github.com/springcoolers/weekly-presentation/assets/49356933/97592832-d298-4bd1-831f-105eb0d43a77)


## Bard에 던지기

![image](https://github.com/springcoolers/weekly-presentation/assets/49356933/3b31d236-c530-4dc1-b60a-c0cabb5916b8)

뭔가 토탈 서치 카운트가 이상합니다. 
![image](https://github.com/springcoolers/weekly-presentation/assets/49356933/a1a3dc5a-f49b-4128-acd0-92a892902aa9)



## 좋아 문제는

- bard가 google knowledge graph, google trend랑 연동할 수 있다는
    - [ ]  구글 트렌드와 연동이 좀 이상한 것 같음. 나의 프롬프트 문제인지, trend랑 연동하는게 애초에 문제인지, 아니면 원하는 데이터가 없는지 확인하기
- 어떤 데이터를 가져다 달라고 할까?
    - 총 검색 숫자
    - 트렌딩 - 최근 몇일간 트렌드가 올랐는지, 요주의 단어가 된 적 있는지
- Dictionary 구축.
    - 이 딕셔너리를 GKG로 대체해볼까 생각중.

## 워너비: Self-constructing Wikipedia - Golden

- 스스로 업데이트 하는 위키피디아 프로덕트를 찾음 ([링크](https://golden.com/product/lists))

# 오늘의 피드백

- [ ]  용선님: 기간별로 tokenizer 학습시켜서 비교했을 것 같다.
- 토크나이저 A,B에 뭐가 들어있는지를 바로 본다. (모델X)
- [ ]  토크나이저 학습에 유효한 데이터 개수! → 트라이 앤 에러

- [ ]  기훈님: token classification 문제로 접근해 보자.
    - 기존 어휘 / 신조어
    - 사람 이름을 잘 태깅하는 모델이면, 새로 나온 아이돌 이름도 잘 태깅할 수 있지 않을까?

- 일정 기간 발생한 신조어 → 레이블링 후 학습→ 다음에도 된다?!
    - 조선: 배 만들다 / 나라 (동음이의어)
    - 합성해서 신조어인 경우, 다른 맥락이랑 의미가 있다. 그래서 될 것 같다.

- 수민님: 빈도수 찾는거는 전통적인 방식
    - term-burstness → 최근에 튀는 단어를 찾는 수치가 있다.
    - trigram per 시기별로 빈도수 구함.
        - 평균적인 증가율보다, 이 기간동안 증가율이 유난히 높다→ Burst!
        - 이미 논문이 잘 나온 분야다
- 2번을 먼저 한다음에, 증가율이 보이면, 그때 얘 정보를 확인하면 된다.
