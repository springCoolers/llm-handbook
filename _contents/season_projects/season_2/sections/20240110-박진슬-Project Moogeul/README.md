# 깃잔심 2+3 최종 발표

# 1. 프로젝트 요약

![example]( )

 

### 목적

- 글에 내포된 감정을 추출하고 그 감정을 통해 되돌아 볼 수 있는 서비스 생성
- 자연어 처리와 관련된 여러가지 태스크를 경험하고, 그 중 해당 서비스에 적용할 수 있는 부분을 적용

### 기능

- 글을 쓰고 싶어하는 사람들에게 글을 작성할 수 있는 공간을 제공
- 에세이 한편이 완료되면, 작성자의 감정을 분석하고 그 감정과 관련된 단어 통계를 제공

### 기대효과

- 사용자는 자기 자신의 단어 사용 행태를 파악할 수 있다
- 저자 별 단어-감정 사용 행태 비교를 통해 특징을 찾아낼 수 있다

# 2. 결과

[Project Moogeul - a Hugging Face Space by seriouspark](https://huggingface.co/spaces/seriouspark/project-moogeul)

## 서비스 구조

프로세스

| 내용 | 필요 데이터셋 | 필요 모델링 | 기타 필요항목 |
| --- | --- | --- | --- |
| 1. 단어 입력 시 에세이 1편을 쓸 수 있는 ‘글쓰기’ 공간 제공 | 네이버 한국어 사전 | - | streamlit 대시보드 |
| 2. 에세이 내 문장 분류 | 한국어 감정분석 자료 58000여건 | xlm-roberta | - |
| 3. 문장 별 감정 라벨 반환 | 한국어 감정분석 자료 58000여건 + 라벨 단순화 (60개 → 6개) | Bert Classifier |  |
| 4. 문장 내 명사, 형용사를 konlpy 활용하여 추출 | 한국어 감정분석 자료 58000여건 | konlpy Kkma | huggingface - pos tagger 검토 |
| 5. 명사, 형용사와 감정 라벨을 pair 로 만들어 빈도 집계 | - | - | - |
| 6. 해당 빈도 기반의 리뷰 제공 (저자 & 에세이리스트 수집) | 칼럼 수집 
(은유, 정이현, 듀나, 총     건) | - | selenium / request / BeutifulSoup |

# 3. 서비스 사용 프로세스

## 1. 글쓰기

- 네이버 사전으로부터 받은 response 를 parsing
- 유저 **단어** 입력 → **사전 속 유사단어 리스트** 반환
- **사전 속 유사단어** 입력 → **사전 속 유사뜻 리스트** 반환

## 2.글 분석하기

- QA모델 활용해 **문장 → 감정 구**
- SentenceTransformer 활용해 **감정 구 → 임베딩**
- 분류모델 활용해 **(임베딩 - 라벨)** 학습
- roberta 활용해 **명사,형용사 추출**

# 4. 테스트 히스토리

### 1. QA모델

```jsx
model_name = 'AlexKay/xlm-roberta-large-qa-multilingual-finedtuned-ru'
question = 'what is the person feeling?'
context = '슬퍼 아주 슬프고 힘들어'
question_answerer = pipeline(task = 'question-answering',model = model_name)
answer = question_answerer(question=question, context=context)

print(answer)
```

{'score': 0.5014625191688538, 'start': 0, 'end': 13, 'answer': '슬퍼 아주 슬프고 힘들어'}

- xlm-roberta-large-qa 모델구조
    - xlm : cross-lingual language model
        
        [참고자료](https://ariz1623.tistory.com/309)1 
        
        - 다국어를 목표로 사전학습 시킨 bert를 교차언어모델(xlm) dlfkrh qnfma
        - xlm 은 단일 언어 및 병렬 데이터셋을 사용해 사전학습
        - 병렬 데이터셋은 언어 쌍의 텍스트로 구성(동일한 내용의 2개 다른 언어 텍스트)
        - BPE를 사용하고 모든 언어에서 공유된 어휘를 사용
        - 사전 학습 전략
            - 인과언어모델링 CLM : 이전 단어셋에서 현재 단어의 확률을 예측
            - 마스크언어모델링 MLM : 토큰 15%를 무작위로 마스킹 후, 마스크된 토큰 예측 (80%은 [mask]로 교체, 10%는 임의 무작위 단어로 교체, 10%는 변경하지 않음
            - 번역 언어모델링 TLM : 서로 다른 언어로서 동일한 텍스트로 구성된 병렬 교차 언어모델을 이용
        - XLM-RoBERTa : 병렬 데이터셋을 구하기에 자료가 적은 언어를 학습하기 위해, MLM으로만 학습시키고 TLM은 사용하지 않음
    - qa 모델
        
        [참고자료](https://huggingface.co/tasks/question-answering) [노트북](https://github.com/huggingface/notebooks/blob/main/examples/question_answering.ipynb)
        
        - 학습 시 QG(question  generation) 과 QA(Question Answer) 부분으로 나뉨
    - config.json
        
        ```jsx
        {
          "_name_or_path": "AlexKay/xlm-roberta-large-qa-multilingual-finedtuned-ru",
          "architectures": [
            "XLMRobertaForQuestionAnswering"
          ],
          "attention_probs_dropout_prob": 0.1,
          "bos_token_id": 0,
          "eos_token_id": 2,
          "gradient_checkpointing": false,
          "hidden_act": "gelu",
          "hidden_dropout_prob": 0.1,
          "hidden_size": 1024,
          "initializer_range": 0.02,
          "intermediate_size": 4096,
          "language": "english",
          "layer_norm_eps": 1e-05,
          "max_position_embeddings": 514,
          "model_type": "xlm-roberta",
          "name": "XLMRoberta",
          "num_attention_heads": 16,
          "num_hidden_layers": 24,
          "output_past": true,
          "pad_token_id": 1,
          "position_embedding_type": "absolute",
          "transformers_version": "4.6.1",
          "type_vocab_size": 1,
          "use_cache": true,
          "vocab_size": 250002
        }
        ```
        
    - RoBERTa
        - 트랜스포머 모델: RoBERTa는 BERT와 마찬가지로 트랜스포머 모델
        - 양방향 컨텍스트: RoBERTa는 문장의 양방향 컨텍스트를 고려
        - 대규모 데이터셋과 긴 트레이닝: RoBERTa는 BERT보다 더 많은 데이터와 더 긴 트레이닝 시간을 사용하여 모델을 훈련
        - BERT의 트레이닝 과정에 포함된 NSP 태스크를 RoBERTa는 제거
        
        ![example]( )
        
- 학습 데이터셋
    - Fine tuned on English and Russian QA datasets

```
model_name = 'monologg/koelectra-base-v2-finetuned-korquad'
question = 'what is the person feeling?'
context = '슬퍼 아주 슬프고 힘들어'
question_answerer = pipeline(task = 'question-answering',model = model_name)
answer = question_answerer(question=question, context=context)

print(answer)
```

{'score': 0.6014181971549988, 'start': 6, 'end': 13, 'answer': '슬프고 힘들어'}

- koelectra-base 모델구조
    
    ![example]( )
    
    [참고자료](https://tech.scatterlab.co.kr/electra-review/)1, [논문](https://arxiv.org/abs/2003.10555)
    
    - electra
        - 2020 구글 리서치 팀에서 발표한 모델
        - Efficiently Learning an Encoder that Classifies Token Replacements Accurately
        - BERT의 경우, 많은 양의 컴퓨팅 리소스를 필요로함
            - 하나의 문장에서 15%만 마스킹하기 때문에, 실제 학습하는 토큰이 15%
        - 입력을 마스킹 하는 대신, 소규모 네트워크에서 샘플링된 그럴듯한 대안으로 토큰을 대체함으로써 입력을 변경
        - 손상된 토큰의 원래 신원을 예측하는 모델을 훈련하는 대신, 손상된 입력의 각 토큰이 생성기 샘플로 대체되었는지 확인
            - original token VS replaced token 맞추는 것 간의 차이발생
    
    **⇒ Robert 와 비슷한 성능을 내면서 1/4 미만의 컴퓨팅 자원을 활용**
    
- 학습 데이터셋 : [참고링크](https://monologg.kr/2020/05/02/koelectra-part2/)
    - SKT의 KoBERT
    - TwoBlock AI의 HanBERT
    - ETRI의 KorBERT
    
    → 한자, 일부 특수문자 제거 / 한국어 문장 분리기 (kss) 사용 / 뉴스 관련 문장은 제거 (무단전재, (서울=뉴스1) 등 포함되면 무조건 제외)
    
- 최종 결과
    
    
    | index | score | start | end | answer |
    | --- | --- | --- | --- | --- |
    | 일은 왜 해도 해도 끝이 없을까? 화가 난다. | 0.9913754463195801 | 19 | 24 | 화가 난다 |
    | 이번 달에 또 급여가 깎였어! 물가는 오르는데 월급만 자꾸 깎이니까 너무 화가 나. | 0.5683395862579346 | 41 | 45 | 화가 나 |
    | 회사에 신입이 들어왔는데 말투가 거슬려. 그런 애를 매일 봐야 한다고 생각하니까 스트레스 받아. | 0.9996705651283264 | 45 | 49 | 스트레스 |
    | 직장에서 막내라는 이유로 나에게만 온갖 심부름을 시켜. 일도 많은 데 정말 분하고 섭섭해. | 0.8939215540885925 | 42 | 49 | 분하고 섭섭해 |
    | 얼마 전 입사한 신입사원이 나를 무시하는 것 같아서 너무 화가 나. | 0.5234862565994263 | 32 | 34 | 화가 |
    | 직장에 다니고 있지만 시간만 버리는 거 같아. 진지하게 진로에 대한 고민이 생겨. | 0.9997361898422241 | 31 | 41 | 진로에 대한 고민이 |
    | 성인인데도 진로를 아직도 못 정했다고 부모님이 노여워하셔. 나도 섭섭해. | 0.9988294839859009 | 36 | 39 | 섭섭해 |
    | 퇴사한 지 얼마 안 됐지만 천천히 직장을 구해보려고. | 0.5484525561332703 | 19 | 28 | 직장을 구해보려고 |
    | 졸업반이라서 취업을 생각해야 하는데 지금 너무 느긋해서 이래도 되나 싶어. | 0.9842100739479065 | 7 | 15 | 취업을 생각해야 |
    | 요즘 직장생활이 너무 편하고 좋은 것 같아! | 0.1027943417429924 | 3 | 8 | 직장생활이 |
    | 취업해야 할 나이인데 취업하고 싶지가 않아. | 0.10440643876791 | 7 | 11 | 나이인데 |
    | 면접에서 부모님 직업에 대한 질문이 들어왔어. | 0.9965717792510986 | 5 | 12 | 부모님 직업에 |
    | 큰일이야. 부장님께 결재받아야 하는 서류가 사라졌어. 한 시간 뒤에 제출해야 하는데 어디로 갔지? | 0.07094824314117432 | 0 | 5 | 큰일이야. |
    | 나 얼마 전에 면접 본 회사에서 면접 합격했다고 연락받았었는데 오늘 다시 입사 취소 통보받아서 당혹스러워. | 0.998587429523468 | 53 | 58 | 당혹스러워 |
    | 길을 가다가 우연히 마주친 동네 아주머니께서 취업했냐고 물어보셔서 당황했어. | 0.9999895095825195 | 37 | 41 | 당황했어 |
    | 어제 합격 통보를 받은 회사에서 문자를 잘못 발송했다고 연락이 왔어. 너무 당혹스럽고 속상해. | 0.8316713571548462 | 42 | 51 | 당혹스럽고 속상해 |
    | 나 오늘 첫 출근 했는데 너무 당황스러웠어! | 0.9923190474510193 | 17 | 23 | 당황스러웠어 |
    | 이번에 직장을 이직했는데 글쎄 만나고 싶지 않은 사람을 만나서 아주 당황스럽더라고. | 0.4635336995124817 | 38 | 45 | 당황스럽더라고 |

## 2. 임베딩 모델

```jsx
tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
tokenizer .encode('당혹스럽고 속상해')
```

- 임베딩 값 (, 10)
    
    (`[101, 9067, 119438, 12605, 118867, 11664, 9449, 14871, 14523, 102]`)
    
- tokenizer

![example]()

[참고자료](https://riverkangg.github.io/nlp/nlp-bertWordEmbedding/)

```jsx
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer('jhgan/ko-sroberta-multitask')
sentences = ['당혹스럽고 속상해',]
embeddings = encoder.encode(sentences)
print(embeddings)
```

- 임베딩 값 (1, 768) (중략)
    
    [[-0.8137736  -0.37767226 ... -0.4278595  -0.4228025 ]]
    
- SentenceTransformer [참고자료](https://www.sbert.net/docs/publications.html)
    
    ![Untitled]( )
    

```jsx
SentenceTransformer(
  (0): Transformer({'max_seq_length': 128, 'do_lower_case': False}) with Transformer model: RobertaModel 
  (1): Pooling({'word_embedding_dimension': 768, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False})
)
```

## 3. 분류모델

- 평가기준 accuracy (from sklearn.metrics import accuracy_score)
- baseline : 0.17 (label 6개 중 1개 임의 선택될 비율,  1/6)

```python
#1차
class BertClassifier(nn.Module):

  def __init__(self, dropout = 0.3):
    super(BertClassifier, self).__init__()

    self.bert= BertModel.from_pretrained('bert-base-multilingual-cased')
    self.dropout = nn.Dropout(dropout)
    self.linear = nn.Linear(768, 6)
    self.relu = nn.ReLU()

  def forward(self, input_id, mask):
    _, pooled_output = self.bert(input_ids = input_id, attention_mask = mask, return_dict = False)
    dropout_output = self.dropout(pooled_output)
    linear_output = self.linear(dropout_output)
    final_layer= self.relu(linear_output)

    return final_layer

# 2차
model = AutoModelForSequenceClassification.from_pretrained('bert-base-multilingual-cased',  )
```

**accuracy 55.7%**

- bert 모델
    - 다중 언어 모델에 dropout / linear / relu 를 추가한 함수
    - epoch = 2 : 적정 수준 (train / test accuracy 0.55~0.57)
    - epoch = 10 : 과적합 (train accuracy 0.98 / test accuracy = 0.56)
        
        → epoch = 2 에서 학습한 수준과 epoch 10에서 학습한 데이터 패턴이 크게 다르지 않음
        

![example]( )

```jsx
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2,stratify=y)

model = RandomForestClassifier()
model.fit(X_train_features_top50, X_train_label)
prediction = model.predict(X_test_features_top50)
score = accuracy_score(X_test_label, prediction)
print('top50 accuracy: ', score) # 더떨어졌다.

models = [
    RandomForestClassifier(),
    LogisticRegression(max_iter = 5000),
    SVC()
]

grid_searches = []
for model in models:
  grid_search = GridSearchCV(model, param_grid = {}, cv = 5)
  grid_searches.append(grid_search)

for grid_search in tqdm(grid_searches):
  grid_search.fit(X_train_feature, X_train_label)

best_models = []
for grid_search in grid_searches:
  best_model = grid_search.best_estimator_
  best_model.append(best_model)

ensemble_model = VotingClassifier(best_models)
ensemble_model.fit(X_train_feature, X_train_label)
predictions = ensemble_model.predict(X_test_feature)
accuracy = accuracy_score(X_test_label, predictions)
```

**accuracy 60.3%**

- [RandomForestClassifier](https://medium.com/analytics-vidhya/random-forest-classifier-and-its-hyperparameters-8467bec755f6)

![example]( )

- [LogisticRegression](https://medium.com/@martinpella/logistic-regression-from-scratch-in-python-124c5636b8ac)

![Untitled]( )

- [SVC](https://scikit-learn.org/stable/modules/svm.html)

![example] )

## 4. 명사/형용사 추출

```python
from konlpy.tag import Okt

okt = Okt()

def get_noun(text):
  noun_list = [k for k, v  in okt.pos(text) if (v == 'Noun' and len(k) > 1)]
  return noun_list
def get_adj(text):
  adj_list = [k for k, v  in okt.pos(text) if (v == 'Adjective') and (len(k) > 1)]
  return adj_list
def get_verb(text):
  verb_list = [k for k, v  in okt.pos(text) if (v == 'Verb') and (len(k) > 1)]
  return verb_list

text = '어제 합격 통보를 받은 회사에서 문자를 잘못 발송했다고 연락이 왔어. 너무 당혹스럽고 속상해.'

get_noun(text)
get_adj(text)
get_verb(text)
```

get_noun: `['어제', '합격', '통보', '회사', '문자', '잘못', '발송', '연락']`

get_adj: `['당혹스럽고', '속상해']`

get_verb: `['받은', '했다고', '왔어']`

- [OKt](https://konlpy.org/en/latest/api/konlpy.tag/#okt-class)

```python
tokenizer=AutoTokenizer.from_pretrained("KoichiYasuoka/roberta-large-korean-upos")
posmodel=AutoModelForTokenClassification.from_pretrained("KoichiYasuoka/roberta-large-korean-upos")

pipeline=TokenClassificationPipeline(tokenizer=tokenizer,
                                     model=posmodel,
                                     aggregation_strategy="simple",
                                     task = 'token-classification')
nlp=lambda x:[(x[t["start"]:t["end"]],t["entity_group"]) for t in pipeline(x)]
nlp(text)

# result
[('어제 합격', 'NOUN'),
 ('통보를', 'NOUN'),
 ('받은', 'VERB'),
 ('회사에서', 'ADV'),
 ('문자를', 'NOUN'),
 ('잘못', 'ADV'),
 ('발송했다고', 'VERB'),
 ('연락이', 'NOUN'),
 ('왔어', 'VERB'),
 ('.', 'PUNCT'),
 ('너무', 'ADV'),
 ('당혹스럽고', 'CCONJ'),
 ('속상해', 'VERB'),
 ('.', 'PUNCT')]
```

- [roberta-large](https://github.com/KLUE-benchmark/KLUE) → KLUE → 한문 교육용 기초 한자 & 인명용 한자를 추가
- RoBERTa(Robustly optimized BERT approach)
    - 
    - [https://huggingface.co/klue/roberta-large](https://huggingface.co/klue/roberta-large)
        
        [https://huggingface.co/KoichiYasuoka/roberta-large-korean-hanja](https://huggingface.co/KoichiYasuoka/roberta-large-korean-hanja)
        
- [데이터셋](https://huggingface.co/KoichiYasuoka/roberta-large-korean-upos/raw/main/vocab.txt)

```jsx
from konlpy.tag import Okt

okt = Okt()

def get_noun(text):
  noun_list = [k for k, v  in okt.pos(text) if (v == 'Noun' and len(k) > 1)]
  return noun_list
def get_adj(text):
  adj_list = [k for k, v  in okt.pos(text) if (v == 'Adjective') and (len(k) > 1)]
  return adj_list
def get_verb(text):
  verb_list = [k for k, v  in okt.pos(text) if (v == 'Verb') and (len(k) > 1)]
  return verb_list

text = '어제 합격 통보를 받은 회사에서 문자를 잘못 발송했다고 연락이 왔어. 너무 당혹스럽고 속상해.'

get_noun(text)
get_adj(text)
get_verb(text)
```

get_noun: `['어제', '합격', '통보', '회사', '문자', '잘못', '발송', '연락']`

get_adj: `['당혹스럽고', '속상해']`

get_verb: `['받은', '했다고', '왔어']`

- [OKt](https://konlpy.org/en/latest/api/konlpy.tag/#okt-class)

# 4. **분석 리포트**

### 1. 저자 분석 가이드라인

- 총 발행 글 수
    - 글 당 문장 수
        1. 글 속 문장 갯수
        2. 글 속 단어 갯수
            
            명사 수 / 형용사 수
            
        3. 문장 기준 최고 감정
        4. 단어 기준 최고 감정
        5. 단어 별 감정 갯수
    - 글 별 감정 / 단어 (명사, 형용사)
        - 감정 1건당 단어 유니크 수 : 가장 다채로운 단어를 사용한 감정은 ?
        - 감정 1건 당 최다 단어 : 그 감정을 대표하는 단어는? / 어떤 단어를 쓸 때 그 감정이 많이 올라왔을까?
        - 단어 1건당 유니크 감정 : 가장 복잡한 감정을 만들어낸 단어는?
        - 단어 1건당 최다 감정 : 그 단어를 쓸 때 어떤 감정이 많이 올라왔을까?

### 2. **예시**

- 에세이스트 <은유> / 총 17개의 에세이 수집 (중략)
    
    ```python
    # 제목 : 사랑에 빠지지 않는 한 사랑은 없다
    
    영화 <나의 사랑, 그리스>의 한 장면
    
    한 사람에게 다가오는 사랑의 기회에 관심이 많다....
    "사랑에 빠지지 않는 한 사랑은 없다. "(151쪽) 사랑은 특별한 지식이나 기술이 필요치 않다는 점에서 쉽고, 자기를 내려놓아야 한다는 점에서 어렵다.
    그러니 사랑을 얼마나 해보았느냐는 질문은 이렇게 바꿀 수도 있다. 당신은 다른 존재가 되어보았느냐. 왜 사랑이 필요하냐고 묻는다면,
    비활성화된 자아의 활성화가 암울한 현실에 숨구멍을 열어주기 때문이라고 답하겠다. 존재의 등이 켜지는 순간 사랑은 속삭인다. “삶을 붙들고 최선을 다해요. ”(123쪽)
    
    ```
    
- 총 발행 글 수 : 17건
- 70.35 문장 / 1글
- 글 속 문장 개수

| title | 문장 수 |
| --- | --- |
| '불쌍한 아이' 만드는 '이상한 어른들' | 53 |
| 글쓰기는 나와 친해지는 일 | 62 |
| 나를 아프게 하는 착한 사람들 | 65 |
| 다정한 얼굴을 완성하는 법 | 65 |
| 딸에 대하여, 실은 엄마에 대하여 | 68 |
| 마침내 사는 법을 배우다 | 64 |
| 만국의 싱글 레이디스여, 버텨주오\! | 69 |
| 문명의 편리가 누군가의 죽음에 빚지고 있음을 | 87 |
| 사랑에 빠지지 않는 한 사랑은 없다 | 63 |
| 성폭력 가해자에게 편지를 보냈다 | 83 |
| 슬픔을 공부해야 하는 이유 | 70 |
| 알려주지 않으면 그 이유를 모르시겠어요? | 67 |
| 우리는 왜 살수록 빚쟁이가 되는가 | 73 |
| 울더라도 정확하게 말하는 것 | 77 |
| 인공자궁을 생각함 | 79 |
| 친구 같은 엄마와 딸이라는 환상 | 80 |
| 하찮은 만남들에 대한 예의 | 88 |
- 글 속 단어 개수

![example]( )

- 문장 기준 최고 감정
    - 에세이를 구성하는 문장의 감정 라벨을 집계
    - ‘**글쓰기는 나와 친해지는일’** 이라는 에세이에서는 [불안] 이 가장 높으며 [기쁨] 과 [분노] 가 그 다음 감
    
    → 문장 분류 모델의 정확도 상승시, 해당 방식으로 에세이 별 ‘주요 감정’ 을 쉽게 구분 및 비교할 수 있음
    
    ![example]( )
    
- **단어 기준 최고 감정 / 단어 별 감정 개수**
    - 명사와 형용사를 합쳤을 경우, 아니라/없는 등의 단어들이 상위에 위치
    - 명사만 추출 시, 2개 이상의 감정이 담긴 단어는 찾지 못함
    
    → 더 많은 에세이를 수집 / lemmatized 된 단어를 사용해 의미 기준으로 재구성이 가능해보임
    

[명사 + 형용사]

![example]( )

- 가장 다채로운 단어를 사용한 감정은 ? (감정 별 문장 1건당 단어)
    - [불안] 단어 종류가 954건으로 가장 많음
    - 문장 수로 나눠보았을 때, [당황] 의 감정이 3.24건으로 문장 1건에서 3개 이상의 단어들이 추출되어 매핑
    
    | emotion | vocab_cnt | sentence_cnt | vocab_per_sentence |
    | --- | --- | --- | --- |
    | 불안 | 954 | 327 | 2.917431 |
    | 슬픔 | 681 | 245 | 2.779592 |
    | 분노 | 736 | 260 | 2.917431 |
    | 기쁨 | 541 | 197 | 2.746193 |
    | 당황 | 318 | 98 | 3.244898 |
    | 상처 | 272 | 86 | 3.162791 |
- 그 감정을 대표하는 단어는? / 어떤 단어를 쓸 때 그 감정이 많이 올라왔을까? (감정 1건 당 최다 단어)
    - [당황] 의 경우 부끄러운, 이상한 이라는 단어가 상위에 존재
    - 그 외의 감정의 경우, 단어로 특성을 찾기 어려움
    
    → 빈도가 높은 단어들이 상위에 존재하여, 해당 방식으로 추출 뒤 tfidf 등의 빈도 기반 스코어로 단어 추가 정렬이 가능해보임
    
    ![example]( )
    
- 가장 복잡한 감정을 만들어낸 단어는? (단어 1건당 유니크 감정)
    - 있는, 없는, 있는, 있다 등이 가장 많이 등장하였고, 그에 따른 감정종류도 가장 많음
    - 단어 맥락에 따라 어느 부분에나 쉽게 적용될 수 있기 때문에 해당 값들이 모든 감정을 가지고 있음
    
    → 복잡한 감정의 기준을 다시 제시하고 (예: 상충되는 감정 ) 그에 따른 ‘복잡한 감정' 과 ‘단어’ 조합을 찾아볼 수 있음
    
    ![example]( )
    
    ![example]( )
    
- 그 단어를 쓸 때 어떤 감정이 많이 올라왔을까? (단어 1건당 최다 감정)
    - [좋아하는] 단어의 경우, 불안 :2 , 기쁨 : 1 , 상처 : 1
    - [부끄러운] 단어의 경우, 당황 : 4
    - [나약한] 단어의 경우 기쁨 : 1
    
    ![example]( )