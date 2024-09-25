# 서수민 - 지식그래프 기초

## 1. 서론 : http://dmqm.korea.ac.kr/activity/seminar/291 발표자료 참고
Knowledge Enhanced NLP.pdf

## 2. 지식그래프란
knowledge graph라는 말은 구글이 만들었다. 2012년 5월 15일 구글에서 영문 검색에 처음 적용했다고 한다. 


head (subject) - relation (predicate) - tail (object) 로 엔티티 사이의 관계를 나타낸다.
예: 뉴진스 - 멤버 - 하니
head (subject) - relation (predicate) - literal 로 엔티티의 정보를 저장할 수도 있다.
예: 뉴진스 - 멤버수 - 5명
데이터 저장방식 측면에서 RDBMS(관계형데이터베이스)와의 차이
RDBMS 인물, 영화, 식당 등등 db별로 다른 스키마를 가지고 다른 테이블에 저장된다. 예를 들어 영화 db의 ‘기생충’에 출연진 값으로 최우식이 들어가 있을 때, 최우식을 인물 db의 최우식과 연결하려면 별도의 조인 작업이 필요하다. 
지식그래프는 주제별로 테이블을 만드는 것이 아니라 모든 지식을 triple로 표현한다. 기생충-출연진-최우식, 최우식-국적-캐나다, 캐나다-수도-오타와… 이런식으로 관계를 찾아나갈 수있다. 
지식그래프는 heterogeneous graph + directional graph
지식그래프는 node(엔티티)를 연결하는 edge(릴레이션)의 성질이 상이한 heterogeneous graph이다. edge의 종류가 국적, 성별, 출연작 등등으로 다양하다. 
또한 방향성을 가진다. 연결 방향에 따라 다른 의미를 가지기 때문이다. 
반면 논문인용 그래프, SNS 팔로우 관계 그래프는 방향성이 있지만 edge의 종류가 하나이다. 친구 관계 그래프를 만든다면 edge의 종류도 하나이고, 방향성은 없다. edge의 종류가 하나인 그래프는 homogeneus 그래프이다. 
homogeneus 그래프에서 통하는 방법들(GNN, GCN 등)이 heterogeneous graph에서는 잘 통하지 않을 수 있으니(edge간 다른 특성을 반영하지 못함) 이 점을 유의해야 한다. 

## 3. 지식그래프 관련 태스크들
https://arxiv.org/abs/2210.00105
https://www.mdpi.com/2078-2489/13/4/161
지식그래프 생성
비정형 텍스트로부터 triple 추출하기 
NER: Named Entity Recognition
RE: Relation Extraction (엔티티 사이의 관계 라벨링 하는 task)
Entity Linking (텍스트를 엔티티랑 매칭하는 task. NER은 person인지 location인지만 분류한다면, Entity Linking은 엔티티를 KB에 있는 엔티티 아이디랑 연결한다.)
reasoning ~= knowledge graph completion ~= link prediction
추론을 통해서 지식그래프에 아직 존재하지 않는 새로운 관계를 찾는 과정.
예를 들어서 a - 아버지 - b, b - 아버지 - c라는 triple이 있으면 이로부터 a - 할아버지 - c 라는 새로운 관계를 찾아낼 수 있다. 
규칙 정의 해서 할 수도 있고 (아버지 두번 타고 가면 할아버지), 지식그래프 임베딩 사용해서 할수도 있다.
기타 application task
KBQA : 지식그래프 활용해서 QA 하기, 챗봇에도 활용 가능
recommendation system : 유저 사용 기록이 없더라도 지식그래프에서 비슷한 성질을 공유하는 엔티티를 추천할 수 있다.
misinformation detection, fake news detection
semantic search : 키워드 검색에서 더 나아가서 지식 그래프 안에서 관련을 가지는 정보를 함께 보여주는 것. 
4. 지식그래프 임베딩
https://towardsdatascience.com/large-scale-knowledge-graph-completion-on-ipu-4cf386dfa826
지식그래프에서도 앞서 말한 여러 태스크에 임베딩 활발히 사용하고 있다. 지식그래프의 노드와 엣지를 임베딩하는 것이다. 
가장 대표적인 heterogeneous 임베딩 알고리즘은 TransE, RotatE


head entity, relation, tail entity 모두 벡터로 표현한다. 올바른 정보를 가진 triple에서는 head entity + relation = tail entity가 나와야 한다. 
TransE는 head entity 벡터에 relation 벡터를 더했을 때 tail vector가 나오도록 모델링하고, RotatE는 head vector를 relation vector 만큼 회전했을 때 tail vector가 나오도록 모델링한다.
triple에 대해 head vector + relation vector - tail vector = 0 이어야 하므로 head vector + relation vector - tail vector를 최소화 하는 것이 목적 함수이다. 
개인적인 의견으로는 application task에서는 임베딩 말고 지식그래프의 명시적인 성질을 그대로 사용하는 것도 강점이 있다고 생각한다. 임베딩은 의미를 뭉쳐서 100%의 정확한 답을 낼 수는 없게 되기 때문이다.

## 5. 지식그래프와 language model
https://arxiv.org/abs/2101.12294
transformer 기반의 language model에 지식그래프를 주입하려는 시도들도 있다. 물론 language model 들도 텍스트 간의 관계를 살펴보면서 semantic을 자연스럽게 파악하겠으나, structured data에서 semantic을 바로 알려주는 것이 성능을 향상시킬 수도 있다는 아이디어

input injection
triple을 텍스트로 만들어서 학습데이터로 쓰기
qa 태스크의 경우 ‘[MASK]는 한국의 수도이다’와 같이 정답인 ‘서울’을 마스킹하고 서울과 지식그래프에서 근처에 있는 부산, 광주 등으로 가짜 정답 만들어 학습 데이터 생성
ERNIE(2019)
bert 인풋으로 token embedding과 엔티티 임베딩(transE) 합쳐서 하나의 임베딩으로 만든다.
엔티티 masking 문제로 바꿔서 bert 구조 그대로 사용. 
relation 맞히기, entity typing 문제에서 더 좋은 성능

## 6. 나무위키로 한국어 지식그래프 만들고 KBQA(Knolwdgebase Question Answering) 하기
영어는 공개된 지식그래프 많음: wikidata(wikipedia 아님), freebase, YAGO, DBpedia
물론 한국어 label을 제공하기 때문에 한국어 엔티티들도 있지만 한국 관련 데이터가 적을수 밖에 없음
나무위키는 2021년 3월까지의 덤프파일 제공한다. (https://mu-star.net/wikidb) 요새는 중단되었음. 
나무위키의 infobox를 사용하여 triple을 추출한다.
