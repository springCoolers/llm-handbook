# 박진슬 CustomerNER

프로젝트 결과

### 1. 데이터셋 수집

- [x]  정신의학칼럼 - 크롤링 - 완료
- [ ]  개인 에세이 글
    - [x]  테스트를 위한 1건 수집 - 완료
        ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/950640f1-e019-4666-a785-1f2ed0283229/Untitled.png)        
    - [ ]  노션 api 확인을 통한 다수 수집 - 진행전

한국어 말뭉치
    - [x]  감성 뭉치 데이터
    - 목적 : 문장과 관련 감정을 학습하기 위한 자료 수집
        - feature : HS~ 로 시작되는 문장 리스트
        - label : [’emotion’][’type’] 의 값
    
    ```jsx
    {'profile': {'persona-id': 'Pro_03807',
       'persona': {'persona-id': 'A02_G01_C01',
        'human': ['A02', 'G01'],
        'computer': ['C01']},
       'emotion': {'emotion-id': 'S06_D02_E36',
        'type': 'E36',
        'situation': ['S06', 'D02']}},
      'talk': {'id': {'profile-id': 'Pro_03807', 'talk-id': 'Pro_03807_00028'},
       'content': {'HS01': '취업을 한다 해도 과연 안정적으로 돈을 벌 수 있을지 회의감이 들어.',
        'SS01': '안정적으로 돈을 벌 수 있을지 회의감이 드는군요. 어떤 점에서 회의감이 드셨나요?',
        'HS02': '내가 남들보다 사회성이 좀 떨어지는 것 같아.',
        'SS02': '사회성이 부족하다고 느끼시는군요. 어떤 일을 하면 사용자님이 더 편안하게 할 수 있을까요?',
        'HS03': '다른 사람들과 같이하는 일보다는 혼자서 하는 일이 더 좋아.',
        'SS03': '혼자서 진행할 수 있는 일을 더 선호하시는군요.'}}},
     {'profile': {'persona-id': 'Pro_03808',
       'persona': {'persona-id': 'A02_G01_C01',
        'human': ['A02', 'G01'],
        'computer': ['C01']},
       'emotion': {'emotion-id': 'S06_D02_E37',
        'type': 'E37',
        'situation': ['S06', 'D02']}},
      'talk': {'id': {'profile-id': 'Pro_03808', 'talk-id': 'Pro_03808_00038'},
       'content': {'HS01': '이번 프레젠테이션도 다른 부서보다 부진할 것 같아 불안해.',
        'SS01': '이번 프레젠테이션도 부진할까 봐 걱정이군요. 어떤 점에서 특히 불안하게 느끼나요?',
        'HS02': '프레젠테이션 내용이 빈약한 것 같아서 걱정이야.',
        'SS02': '발표 내용이 빈약할까 봐 걱정스러워하는군요. 어떻게 하면 내용을 더 발전시킬 수 있을까요?',
        'HS03': '팀원들과 한 번 더 회의를 해봐야겠어.',
        'SS03': '팀원들과 회의를 한 번 더 가질 계획이군요.'}}},
    ```

### 2. 데이터 전처리

    - 필요 데이터 셋 형태
        - 예시
            - [https://github.com/kmounlp/NER/blob/master/말뭉치 - 형태소_개체명/00002_NER.txt#L7](https://github.com/kmounlp/NER/blob/master/%EB%A7%90%EB%AD%89%EC%B9%98%20-%20%ED%98%95%ED%83%9C%EC%86%8C_%EA%B0%9C%EC%B2%B4%EB%AA%85/00002_NER.txt#L7)
            
            ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ec9b73ad-1ba2-4d45-a555-4f59b02f7805/Untitled.png)
            
    - 진행하고자 하는 전처리
        - 이번 프레젠테이션도 부진할까 봐 걱정이군요
            
            ```python
            이번           O
            프레젠테이션도  B-걱정
            부진할까       O
            봐             O
            걱정이군요      B-걱정
            ```
            
    - 각 문장별 감정과, 문장 내 ‘태깅 대상’과 매칭
        - 문장별 감정 : 감정 라벨링으로 진행
        - 문장 내 태깅 대상 선정 :
            - 문장 ‘동사(ROOT)’ 와 dependency parsing 을 할 때 연결된 단어 중'nsubj', 'obj','csubj','nmod’, ‘compound’ 만 수집
                
                ```python
                {0: {'흐른다': ['땀이']},
                 1: {'흐르고': ['줄기를', '땀이', '가슴을', '명치를', '지나고']},
                 2: {'하고': ['선풍기를', '찾기']},
                 3: {'하지 않는다': ['핸디 선풍기는', '공간을']},
                 4: {'하지 않는다': ['사이즈의', '충전 구멍을', '구멍을', '선을']},
                 5: {'본다': ['선풍기를', '앞 뒤']},
                 6: {'돌아가는지': ['버튼을', '연속 번', '팬이']},
                 7: {'들어오는지': ['빨간불이']},
                ```
            

### 3. 모델링

#### 3-1. 감성 분류 모델
    
    - [**1차]** 1번 데이터로 60개 라벨 다중 분류
        
        ```python
        model_name = 'bert-base-multilingual-cased'
        
        optimizer = optim.AdamW(model.parameters(), lr=0.001)
        criterion = nn.CrossEntropyLoss()
        model = model.to(device)
        
        with tqdm(range(4)) as pbar:
          for e in pbar:
            loss_list = []
            for batch in dl_train:
              batch = {k : v.to(device) for k, v in batch.items()}
              optimizer.zero_grad()
              output = model(**batch)
              loss = output.loss 
              loss_list.append(loss.item())
              loss.backward()
              optimizer.step()
              pbar.set_postfix(avg_loss= np.mean(loss_list))
            model.save_pretrained(f'../content/drive/MyDrive/2023/korean_data/model/sentimetal_classification_epoch{e}/')
        ```
        
    - 결과 : 수렴이 되지 않아 학습 실패 (4.11 수준에 수렴)
    
    - **[2차]** NSMC 학습된 모델로 긍, 부정 추론
        
        ```python
        tokenizer = AutoTokenizer.from_pretrained("daekeun-ml/koelectra-small-v3-nsmc")
        ```
        
    - 결과 : 사전 학습된 모델의 경우, 아래와 같이 판정
        - 눈으로 식별할 때 pos / neg 가 아닌 중립의 문장 확인
        - 중립으로 판정되어야 할  (아아) 문장들의 스코어도 낮은 상태
        
        ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/8bcd5805-1bef-4762-92ff-03ee4760ebda/Untitled.png)
        
    
    3-2. NER 태그 모델
    
    - Spacy 사용
        - 결과 : 에세이에 적용해볼 만큼의 단어 리스트는 부족함
        - 한국어 말뭉치 등을 활용하여 entity 가 태깅 될 대상의 수를 늘려야 한다는 판단
            
            ```python
            한 줄 26 29 QT
            한번 24 26 QT
            두 번 35 38 QT
            주말에 11 14 DT
            오늘 0 2 DT
            하루는 3 6 DT
            여름을 23 26 DT
            내년의 4 7 DT
            ```
            
    - **Pytorch-BERT-CRF-NER 문서 학습**
        - 링크 : https://github.com/eagle705/pytorch-bert-crf-ner
        - (진행중)

### 4. (현재까지의 ) 결과 :

    - NER 에 넣을 수 있는 초기 데이터셋 구축
        
        ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ed912e81-b458-47b8-a230-1fd0e69238fe/Untitled.png)
        
    - 참고자료 데이터셋과 같은 형태로 변경
        
        ![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/2f6bd6cd-7d2d-4b61-8ce5-f38f5e49904b/Untitled.png)
    

### 5. 후속작업

    - 60개 감정 다중 분류 모델 학습 후 문장 별 추론
    - 저자 1명의 에세이 글 전체를 수집하여, 데이터셋 별 감정 데이터셋으로 파인튜닝
