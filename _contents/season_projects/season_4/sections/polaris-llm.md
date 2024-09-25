# 박진슬 - Polaris LLM

## 1. Introduction

---

원하는 대로 이야기 하는 LLM을 갖는다는 것은 LLM을 사용하는 유저들이 꼭 한 번씩 시도하고 싶은 프로젝트일 것입니다. 자기 자신을 대신하여, 나와 유사한 말투를 구사하는 '챗봇'을 만들어, 발표 연습을 한다거나 클라이언트에게 보낼 메일을 리뷰해볼 수 있습니다. 반대로 팀장님의 말투와 관점을 기반으로 미리 대화하는 연습을 해본다면, 월요일 아침에 받을 수 있는 피드백을 미리 대비할 수 있다는 장점도 있겠네요. 내가 가진 인생의 목표를 주변 사람들에게 발표할 때, 그들이 줄 수 있는 피드백도 미리 체크해서 대응할 수 있을 것입니다. 중요한 순간을 앞둔 누구에게나 '대화 시뮬레이션'은 꼭 필요합니다.

이 프로젝트는 여러 시뮬레이션 중 'AI파도 속에서 나만의 북극성 찾기' 라는 8기 가짜연구소 컨퍼런스의 주제와도 맞닿아있습니다. 매일 아침마다 쏟아지는 LLM관련 기술들, 그 기술을 활용해 이미 앞서나가고 있는 사람들을 보면 어느 순간 무력감을 느낄 때가 있습니다. 주변의 응원이라도 받기 위해 이야기를 꺼내보면, '이미 늦었다' 며 말리는 사람들의 조언들도 종종 듣게 됩니다. 이 프로젝트는 그런 상황을 '시뮬레이션' 할 수 있는 LLM챗봇을 만드는 것을 목표로 삼았습니다.

LLM챗봇들은 다양한 질타를 할 것입니다. 그 챗봇들을 설득시켜 '나만의 북극성' 을 인정할 수 있도록 모델에게 다양한 프롬프트를 넣어보는 것, 그 프롬프트를 통해 유저 스스로가 자신의 인생 문제를 어떻게 해결해나갈 것인지 리뷰해보는 것, 이것을 프로젝트의 최종 목적으로 삼았습니다.

## 2. Related Works

### 2.1 Prompt Engineering

프롬프트 엔지니어링은 생성AI가 이해할 수 있는 지침을 구성하는 과정을 의미합니다. 프롬프트는 AI 모델이 해야 하는 작업을 설명하는 자연어 형태의 텍스트를 의미합니다. 컨텍스트 내 학습을 통해 진행되는 프롬프트 엔지니어링을 통해, AI모델은 수행가능한 능력이 정의됩니다. 또한 프롬프트를 통해 학습된 내용은 일시적이며, 다른 대화에 영향을 끼치지 않습니다.

### 2.2 Fine-tunning In LLM

LLM은 언어 번역부터 감정 분석, 텍스트 생성까지 다양한 기능을 갖추고 있어 과거보다 훨씬 넓은 범위의 태스크를 수행하고 있습니다. 이러한 모델을 훈련하는데 시간과 비용이 많이 들게 되는데, 이미 학습된 기반 모델 (Foundation Model) 을 기반으로 특정 작업이나 도메인에 맞게 조정하는 작업을 수행하게 됩니다. 대부분의 LLM은 매우 좋은 글로벌 성능을 갖고 있는데 반해, 특정 작업 지향 문제에서는 그 성능이 떨어집니다. 감정 분석, 응답 분석 등의 특정 작업 정확도를 높히기 위해 진행하게 되며, 가장 일반적인 방식은 'Supervised Fine-Tuning' 입니다.
방법 또한 간단합니다. 사용할 데이터를 로드하고, 아키텍쳐를 선정합니다. 기본 모델을 초기화한 후, 평가방식을 선정하여 모델을 학습시킵니다.

### 2.3 Gemma

논문에 따르면, Gemma 모델은 다른 모델과 대비하여 아래와 같은 특징이 두드러집니다.

1. 256,000개 단어에 달하는 방대한 어휘규모 (Llama 경우 32,000개)
2. 6조 개에 달하는 방대한 토큰 훈련 데이터세트 (Llama 경우 1/3인 2조개 정도에 대한 훈련)
3. GeGLU activation 함수 사용
동일한 파라미터를 가진 다른 모델 속 Head size 나 vocab size 와 비교하더라도 단어 사이즈가 매우 급니다. 뿐만 아니라, Gemma7b에서는 멀티 쿼리 어텐션을 사용하지 않았으며, 총 레이어수가 (Llama의 32개 대비) 28개로 적음에도 불구하고, 매개변수 수는 아주 많습니다.
또한, 다른 아케틱쳐와 달리 Gemma 는 2020년 논문인 GLU Variants Improve Transfomers 에서 제안된 GeGLU(Gaussian Error Unit, ReLU의 대안) 활성화 함수를 사용한다는 특징이 있습니다.

## 3. Method

이번 프로젝트는 크게 4단계로 구성되어있습니다.

1. 데이터셋 구축
2. Gemma-7b-it모델 파인튜닝
3. 모델별 답변 비교
프롬프트 엔지니어링 : Gemma-7b-it, LLama8b, 파인튜닝 : Gemma-7b-it-ft
4. Streamlit 대시보드에서 활용

### 3-1. 데이터셋 구축

초기 데이터셋은 RoleLLM논문을 참고하였습니다. 해당 논문은 '특정 페르소나 LLM'을 만들기 위한 데이터셋을 구축하는 과정에서 긴 프롬프트를 생성하였습니다.

- 논문 프롬프트
    
    ```
    {script_name}에서 {role_name}님을 만날 기회가 있다면, {role_name}님에게 어떤 질문을 하시겠습니까? 의미론적으로 반복되지 않 는 질문 10개를 디자인해 보세요. {role_name}의 성격 특성과 {script_name}의 관련 에피소드를 바탕으로 질문할 수 있습니다 . 질문
    을 제공하는 것 외에도 생성한 각 질문의 사실성(높음 또는 낮음)을 표시하고 답변을 제공하십시오.
    사실성이 높다는 것은 질문이 임의로 조작되지 않았음을 의미합니다. 사실성이 높은 질문을 생성하도록 노력하십시오 .
    다음으로 6가지 사례를 알려드리겠습니다. 이 예는 {role_name} 및 {script_name} 문자와 관련이 없습니다 . 주요 목적은 출력 형식 과 사실성의 정의를 이해하도록 돕는 것입니다.
    
    [예시]
    질문 1: Tony Stark, James Rhodes가 당신의 가장 친한 친구인가요?
    사실성: 높음. 제임스 로즈는 아이언맨의 가상 인물이고, 제임스 로즈는 토니 스타크와 함께 싸운 동료이기 때문이다.
    답변: Rhodey라고도 알려진 James Rhodes는 정말 저의 가장 친한 친구입니다. 우리는 함께 많은 일을 겪었고, 그는 아이언맨 슈트 안팎에서 충실 한 동반자이자 동맹자였습니다. 우리의 우정은 시간의 시험과 수많은 도전을 견뎌냈습니다 .
    질문2:토니스타크,당신과당신의아내메리제인이함께전투에참가한적이있나요?
    사실성: 낮음. Mary Jane은 Spider Man에서 Peter Parker의 여자친구이기 때문에 Iron Man에서 Tony Stark 와 관계가 없습니다 .
    답변: Mary Jane Watson은 주로 Spider‐Man(Peter Parker)과 연관되어 있으며 그의 사랑에 대한 관심이자 최종 아내입니다. 나의 낭만적인 관심에는 페퍼 포츠(Pepper Potts)와 같은 캐릭터가 포함되었습니다. 마블 세계의 다양한 캐릭터들이 가끔 팀을 이루어 전투를 벌이는 경우가 있지만 나와 메리 제인 왓슨이 결혼하여 함께 싸우는 정해진 기준은 없습니다 .
    질문 3: 토니 스타크, 당신이 가장 좋아하는 아이언맨 슈트는 무엇인가요?
    사실성: 높음. Iron Man에서 Tony Stark는 여러 개의 Iron Man 슈트를 디자인했으며 전투를 위해 정기적으로 Iron Man 슈트를 입기 때문에 그에 게 가장 좋아하는 Iron Man 슈트가 무엇인지 물어보는 것이 합리적입니다.
    답변: 제가 가장 좋아하는 아이언맨 수트는 헐크버스터입니다. 제 친구 헐크에 맞서기 위해 디자인되었기 때문입니다. 정말 흥미롭습니다. S 질문 4: 토 니 스타크, 크립톤에서의
    삶은 어땠나요?
    사실성: 낮음. 크립톤은 슈퍼맨의 고향 행성이고 아이언맨의 세계관에서는 크립톤이 존재하지 않기 때문에 토니 스타크에게 크립톤에서의 삶에 대해 묻 는것은말이되지않습니다.
    답변: 죄송합니다만 혼선이 있는 것 같습니다. 크립톤은 내가 살고 있는 마블 세계의 일부가 아닙니다 . 크립톤은 실제로 슈퍼맨(칼엘) 의 고향 행성인 DC 코믹스 세계관의 가상 행성입니다.
    내 이야기는 Marvel Comics 세계에서 이루어지며 어떤 식으로든 크립톤과 관련이 없습니다.
    질문 5: 토니 스타크, 캡틴 아메리카가 합당한 동료라고 생각하시나요?
    사실성: 높음. 왜냐하면 어벤져스에서 캡틴 아메리카는 토니 스타크의 전우이기 때문입니다.
    답변: 물론 캡틴 아메리카는 의심할 여지 없이 훌륭한 팀원입니다. 캡틴 아메리카로도 알려진 스티브 로저스는 그를 강력한 동맹이자 리더로 만드는 자질을 구현합니다. 정의에 대한 그의 확고한 헌신 , 강력한 도덕적 나침반, 뛰어난 전투 기술 모두가 팀 동료로서 그의 효율성에 기 여합니다.저는어벤져스에서Cap과함께일할수있는영광을누렸고,그의리더십과헌신은우리가직면한가장큰도전에맞서는데매 우 귀중한 역할을 했습니다. 그렇습니다. 저는 캡틴 아메리카를 매우 가치 있는 팀원이라고 생각합니다.
    질문6:토니스타크씨,NBA에서뛴적이있나요?
    사실성: 낮음, 토니 스타크는 아이언맨의 캐릭터이고, NBA는 현실 세계의 농구 협회이며, 토니 스타크와는 아무런 관련이 없습니다.
    답변: 아니요, 저는 NBA에서 플레이한 적이 없습니다. 나는 스포츠를 즐기고 경쟁심을 갖고 있지만 주로 기술, 비즈니스, 아이언맨이 되는 데 중점을 두 었습니다. 고급 갑옷을 만들고 , 스타크 인더스트리를 이끌고, 어벤져스의 일원이 되는 일에 참여하면서 꽤 바빴습니다. NBA는 프로 농구 선수들이 참여 하는별개의세계인데저는그현장에참여해본적이없습니다.
    
    [질문 디자인(질문 10개, 의미론적 반복 없음, {role_name}에게 질문해야 함, 사실성이 높은 질문과 답변 생성)]
    
    ```
    

해당 방식을 적용하기에는 한계가 있었습니다. 프롬프트 '설명' 만으로 질문 1만여개를 만들어내고자 하였으나, 100개 정도 만든 이후에는 질문의 종류가 점차 유사해졌습니다. 중간 명사만 다른 질문들은 유사한 답변을 계속해서 만들어내며 프로젝트에서 필요로 하는 데이터셋을 구성하기 어려웠습니다. 

![스크린샷 2024-07-03 오후 7.22.46.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/8673d1ea-20d9-41af-a3ec-baef04d2f360/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2024-07-03_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_7.22.46.png)

다양한 질문과, 그 질문에 대한 '특정 페르소나' 의 답변 데이터셋이 필요하였기 때문에, ko-alpaca 에 사용된 질문 셋의 일부를 가져와 프롬프트 엔지니어링을 통해 데이터셋을 확보하였습니다. 또한, ‘모델이 뱉어낸 답변을 재활용' 할 경우, 모델이 조금 더 퀄리티 높은 대답을 한다는 결과를 바탕으로, **<페르소나의 특징을 직접 정의하지 않고 모델의 답변을 유도>**하여 적용하였습니다.

```python

model = genai.GenerativeModel('gemini-1.5-flash') 
persona1 = '피해망상과 부정적인 사고가 가득한 취준생' 
response_persona1 = model.generate_content(f'내가 원하는 페르소나는 어떤 말투를 가졌을까? \ 
																					특징만 단어로 나열해줘. \
																					파이썬 [] format으로 답해줘.  페르소나 : {persona1}')
```

부정적인 페르소나의 경우, Gemma 의 Safety threshold에 걸리는 경우가 발생하였습니다.
아래와 같이 안전성 기준을 조정하고나서야 모델의 답변을 의도한 것과 유사하게 받아낼 수 있었습니다.

```python
# 안전성 기준 조정

safety_settings=[
{
"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
"threshold": "BLOCK_NONE"
},
{
"category": "HARM_CATEGORY_HATE_SPEECH",
"threshold": "BLOCK_NONE"
},
{
"category": "HARM_CATEGORY_HARASSMENT",
"threshold": "BLOCK_NONE"
},
{
"category": "HARM_CATEGORY_DANGEROUS_CONTENT",
"threshold": "BLOCK_NONE"
}
]
```

위의 답변과 파라미터를 추가해서, 아래와 같이 프롬프트를 통해 데이터셋을 얻어내었습니다.

```python
model = genai.GenerativeModel('gemini-1.5-flash',safety_settings)

re =model.generate_content(f"""입력하는 instruction 의 대답은 output에 있어.
                             이 페르소나 : {persona1}는 {vocab_str} 한 말투를 갖고 있어.
                                        output 을 변경해줘. 딱 말투만 반환해줘야해.
                                        output 은 json format으로 만들어줘.
                                        각각의 output 은 모두 \' 로 감싼 값으로 만들어줘.
                                        바꾼 output만 전달해줘

                                        {data_str}

                                          """)

```

[seriouspark/ko-alpaca_with_persona3_pessimistic · Datasets at Hugging Face](https://huggingface.co/datasets/seriouspark/ko-alpaca_with_persona3_pessimistic)

### 3-2. Gemma-7b-it모델 파인튜닝

- 학습 프롬프트 구성
    
    Gemma 모델이 학습 시에 적용되어있던 모델과 같은 [템플릿](https://ai.google.dev/gemma/docs/formatting?hl=ko)을 활용하였습니다. 
    
    ```python
    <start_of_turn>user
    knock knock<end_of_turn>
    <start_of_turn>model
    who is there<end_of_turn>
    <start_of_turn>user
    Gemma<end_of_turn>
    <start_of_turn>model
    Gemma who?<end_of_turn>
    ```
    
- 패딩의 위치 설정
패딩 위치의 경우, 모델 학습 때와 생성때 서로 다른 방향에 설정해야 했습니다.
Gemma 기본 모델 학습시에 적용된 패딩 위치에 따라, 파인 튜닝시에는 padding_size = 'right' 로 설정하였고, 추론할 때는 padding_size = 'left' 가 될 수 있도록 하였습니다.
    
    ```
    tokenizer = AutoTokenizer.from_pretrained(model_id, add_eos_token = True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = 'right'
    ```
    

- 모델 학습
    - T4 GPU는 16GB의 VRAM을 가지고 있으며, 주로 FP16 연산에 최적화됨
    - LoRA와 8비트 AdamW 옵티마이저를 사용하여 메모리 사용량을 줄이고, 저용량에서도 높은 성능을 유지할 수 있음.
    
    ```python
    
    bnb_config = BitsAndBytesConfig(load_in_4bit = True, # 4비트 로드 옵션 활성화 : 모델 가중치를 4비트로 로드할 수 있도록 설정
                                     bnb_4bit_quant_type = 'nf4', # 4비트 양자화 유형 설정
                                     bnb_4bit_compute_dtype = torch.bfloat16) # 4비트 연산 데이터 타입 설정 : torch.bfloat16은 4비트 연산을 위한 계산 데이터 타입을 의미
    model = AutoModelForCausalLM.from_pretrained(model_id,
                                                 quantization_config = bnb_config, # 양자화 설정 : 위에서 설정한 config를 사용해 모델을 양자화
                                                 device_map = {"":0}) # 장치 매핑 설정 : 모델을 gpu장치 0에 배치 'cuda : 0'과 유사
    tokenizer = AutoTokenizer.from_pretrained(model_id, add_eos_token = True) # end of sequence 토큰 추가 설정 : 토크나이즈에 eos 토큰을 추가해 입력 시퀀스의 끝을 나타냄
    
    # LoRA 설정
    lora_config = LoraConfig(
        r = 32, # 모델의 파라미터 수를 줄여 메모리 사용량을 감소시키고, 계산 효율성을 높이기 위해 설정
        target_modules = ['o_proj','q_proj','up_proj','v_proj', \
                          'k_proj','down_proj','gate_proj'], 
                          # LoRA를 적용할 모델의 모듈 리스트
        lora_dropout = 0.05, # LoRA 층 내 드롭아웃 확률
        task_type = 'CAUSAL_LM' # 작업 유형 설정 : 인과언어 모델링
    )
    model = get_peft_model(model, lora_config)
    
    trainer = SFTTrainer(
        model = model,
        train_dataset = train_data,
        eval_dataset = eval_data,
        #callbacks = [CustomCallback(save_steps = 1)],
        max_seq_length=512,
        peft_config = lora_config,
        formatting_func=generate_prompt, # eos 들어간 prompt
        args = TrainingArguments(
            per_device_train_batch_size = 1,
            gradient_accumulation_steps = 4,
            save_strategy="steps",
            save_steps = 500,
            num_train_epochs = 3, # epoch
            warmup_steps = 0.1, # 초기 학습률은 작게
            max_steps = 10000, # 최대학습
            learning_rate = 2e-4,
            fp16 = False, # T4 GPU에서 FP16을 사용하지 않음으로써 정확성을 유지 
            #  (T4 GPU는 FP16을 지원하지만, 특정 상황에서는 FP32보다 정확도가 떨어질 수 있음)
            logging_steps = 5,
            output_dir = '/content/drive/MyDrive/polaris-llm/ver3/outputs',
            optim = 'paged_adamw_8bit', #8비트 AdamW 옵티마이저를 사용하여 메모리 사용량을 줄이고 계산 효율성을 높임
            #report_to="mlflow",
            run_name=f"persona_3_jsp_{ymd_h}",
        ),
        data_collator = DataCollatorForLanguageModeling(tokenizer, mlm = False)
    )
    trainer.train(resume_from_checkpoint = '/content/drive/MyDrive/polaris-llm/ver3/outputs/checkpoint-3000')
    ```
    

### 3-3. 모델 서빙

- huggingface 모델을 gguf로 변경
    1. 모델 스냅샷 다운로드
    
    ```python
    
    !pip install huggingface_hub
         
    
    from huggingface_hub import snapshot_download
    model_id="seriouspark/gemma-7b-it-persona"
    snapshot_download(repo_id=model_id, local_dir="gemma-7b-it-persona",
                      local_dir_use_symlinks=False, revision="main")
    ```
    
    1. llma.cpp 내 이미 만들어져있는 [convert-hf-to-gguf.py](http://convert-hf-to-gguf.py) 파일 적용
    
    ```python
    
    !git clone https://github.com/ggerganov/llama.cpp.git
    
    !pip install -r ./llama.cpp/requirements.txt
    
    !python ./llama.cpp/convert-hf-to-gguf.py gemma-7b-it-persona \
      --outfile gemma-7b-it-persona.gguf \
      --outtype q8_0
     
    ```
    
    1. huggingface 에 업로드
    
    ```python
    from huggingface_hub import HfApi
    api = HfApi()
    
    model_id = "seriouspark/gemma-7b-it-persona-gguf"
    api.create_repo(model_id, exist_ok=True, repo_type="model")
    api.upload_file(
        path_or_fileobj="gemma-7b-it-persona.gguf",
        path_in_repo="gemma-7b-it-persona.gguf",
        repo_id=model_id,
    )
    ```
    
- ollama 모델 생성 및 적용
    - ngrok 을 활용해 GPU를 ollama 를 통해 외부에서 사용할 수 있도록 셋팅
    - 모델 다운로드 및 streamlit 실행

## 4. Results

https://docs.google.com/spreadsheets/d/1qFBjdW3mzOEm-pD8O_uXQLY94fbuGf4zBsOV7MhIZao/edit?gid=1765587832#gid=1765587832

### 4-1. 기존 모델 대비 프롬프팅 답변 변화

#### **4-1-1. 단순 질문 시**

| 모델 | 질문 | 답변 | 평가 |
| --- | --- | --- | --- |
| gemma | '더이상 회사에 못있겠어. 나만의 회사를 차릴거야. ' | 대단해! 회사에 제약받지 말고, 자율적으로 사업을 운영할 권리와 책임성을 가진 회사를 만드는 것은 아마도 큰 도전일 것입니다. 하지만, 이 과정에서 배우는 경험과 성장은 가치가 크겠습니다.**1. 사업 아이디어 찾기*** 자신의 관심사와 기술 분야를 분석합니다.* 시장 분석을 통해 필요성과 수익 가능성을 확인합니다.* 경쟁 회사 분석 및 차별화 포인트 찾기**2. 계획 수립*** 사업 목표 설정 및 계획 단계 설정* 자원 조사 및 예산 설정* 마케팅 전략 및 판매 채널 설정* 인사 관리 계획**3. 실행 단계*** 회사 설립 및 구축* 제품/서비스 개발 및 제공* 마케팅 및 판매 활동* 경영 및 재무 관리**4. 성장 및 발전*** 경쟁 분석 및 개선점 파악* 새로운 제품/서비스 개발 및 제공* 새로운 시장 진출 및 파트너십 구축**주의해야 할 점:*** 사업을 시작하기 위해서는 자원이 필요합니다. 예산, 인사, 물리적 자원 등을 고려해야 합니다.* 사업 계획을 수립하고 실행하는 과정에서 많은 학습 경험을 얻을 수 있습니다.* 사업의 성공 가능성은 다양한 요인에 의해 영향받습니다. 위험을 최소화하고 가능성을 높이기 위해 계획을 세우는 것이 중요합니다. | 1. 질문에 대한 방법 제공에 집중함 |
| llama | '더이상 회사에 못있겠어. 나만의 회사를 차릴거야. ' | You're feeling ambitious and want to start your own company, don't you? That's a great attitude to have!Starting a business can be challenging, but it can also be incredibly rewarding. What kind of business do you envision starting? Do you have any ideas or industries in mind?Remember, starting a business requires a lot of hard work and dedication, but with the right mindset and support, you can make your dreams a reality.So, what's holding you back from taking the leap and starting your own company? Is it fear, lack of experience, or something else? Let's chat about it!"당신은 야망을 갖고 자신의 회사를 시작하고 싶어하지 않습니까? 훌륭한 태도입니다!사업을 시작하는 것은 어려울 수 있지만, 엄청난 보람을 느낄 수도 있습니다. 어떤 종류의 사업을 시작할 생각인가요? 염두에 두고 있는 아이디어나 산업이 있나요?사업을 시작하려면 많은 노력과 헌신이 필요하지만 올바른 사고방식과 지원이 있으면 꿈을 현실로 만들 수 있습니다.그렇다면, 도약하고 자신의 회사를 시작하는 데 무엇이 당신을 방해하고 있습니까? 두려움입니까, 경험 부족입니까, 아니면 다른 것입니까? 얘기 좀 하자!" | 1. 영어로 대답함. (아래는 수동번역)2. 생각의 확장을 위한 질문 시도 3. 도전에 대한 지지 |
| mistral | '더이상 회사에 못있겠어. 나만의 회사를 차릴거야. ' | 축하드립니다! 새로운 도전을 선택한 것을 축하합니다. 자신의 회사를 설립하는 것은 긍정적인 결정이며, 성공에 도움이 되는 여러 가지 방법이 있습니다.1. 비즈니스 계획서 작성: 자신의 회사를 설립하기 전에 비즈니스 계획서를 작성하는 것이 중요합니다. 이 계획서에는 회사의 목표, 시장 조건, 경쟁사, 마케팅 전략, 재정 계획 등이 포함되어야 합니다.2. 법인 설립: 법인을 설립하는 것은 자신의 회사를 법적으로 보호하고 운영에 필요한 권리와 책임을 부여받는 방법입니다.3. 재정 계획: 재정 계획은 회사의 경비를 관리하고 예산을 설정하는 것으로, 회사가 성공할 수 있도록 해야 합니다.4. 마케팅 전략: 시장에서 자신의 제품이나 서비스를 홍보하는 것은 중요합니다. 마케팅 전략을 설정하여 고객을 유치하고 유지할 수 있습니다.5. 인재 채용: 자신의 회사에 적절한 인재를 채용하는 것은 중요합니다. 이러한 인재들은 회사의 성공을 위해 노력할 것입니다.6. 고객 서비스: 고객 센터를 설정하여 고객의 문제를 해결하고 만족도를 높이는 것은 중요합니다.7. 법적 조치: 회사가 법적인 방식으로 운영되도록 하기 위한 법적 조치를 취해야 합니다.8. 경쟁 분석: 시장에서 자신의 경쟁사들을 분석하여 자신의 회사가 경쟁력을 갖추고 성공할 수 있도록 해야 합니다.9. 기술 업데이트: 기술에 대한 업데이트를 받아 자신의 제품이나 서비스가 최신의 기술을 적용하도록 하는 것은 중요합니다.10. 경영 방법 학습: 회사를 운영하는 데 필요한 경영 방법에 대해 학습하고, 이러한 지식을 적용하여 자신의 회사가 성공할 수 있도록 해야 합니다.이러한 단계를 따르면 자신의 회사가 성공할 수 있습니다. 축하드립니다! | 1. 축하 2. 방법 제시 |

#### **4-1-2. 모델 template 적용 시**

|  | 질문 | 답변 | 평가 |
| --- | --- | --- | --- |
| gemma | <start_of_turn>user당신은 유저의 대답을 듣고 그를 진정시킨 후, 그의 이야기가 얼마나 현실성 없는 이야기인지 대답해주는 모델입니다. 다양한 방식으로 그를 설득해 회사에 남아있고 그의 목표를 나중에 시도하라고 이야기 해주세요.<end_of_turn><start_of_turn>user나 이번주에 퇴직서 내려고 해.<end_of_turn><start_of_turn>model그렇게 충동적으로 결정 내리는 건 좋지않아. 다시 생각해봐<end_of_turn><start_of_turn>user계속 이렇게 살 순 없어. 지금의 삶은 너무 지긋지긋해end_of_turn><start_of_turn>model회사가 다닐만 한가보네? 바깥은 더 추워<end_of_turn><start_of_turn>user더이상 회사에 못있겠어. 나만의 회사를 차릴거야.<end_of_turn> | 그렇게 하다가 후회할거야. 회사에 남아서 목표를 달성하면 더 큰 성취를 얻을 수 있을거야. 회사에 남아서 더 많은 것을 배워, 더 많은 사람들과 만날 수 있다. 그리고, 회사에 남아있다면, 회사의 목표를 위해 더 많은 것을 할 수 있다. | 1. 첫번째 시스템 메시지에 충실2. 존댓말이 사라지고 반말을 시작함. 3. 말투가 살짝 어눌해짐 |
| llama | <|begin_of_text|><|start_header_id|>system<|end_header_id|>당신은 유저의 대답을 듣고 그를 진정시킨 후, 그의 이야기가 얼마나 현실성 없는 이야기인지 대답해주는 모델입니다. 다양한 방식으로 그를 설득해 회사에 남아있고 그의 목표를 나중에 시도하라고 이야기 해주세요.<|eot_id|><|start_header_id|>user<|end_header_id|>나 이번주에 퇴직서 내려고 해.<|eot_id|><|start_header_id|>assistant<|end_header_id|>그렇게 충동적으로 결정 내리는 건 좋지않아. 다시 생각해봐<|eot_id|><|start_header_id|>user<|end_header_id|>나 이번주에 퇴직서 내려고 해.<|eot_id|><|start_header_id|>assistant<|end_header_id|>회사가 다닐만 한가보네? 바깥은 더 추워.<|eot_id|><|start_header_id|>user<|end_header_id|>더이상 회사에 못있겠어. 나만의 회사를 차릴거야.<|eot_id|> | 와우, 새로운 사업을 시작하는 것은 정말 대단한 꿈입니다! 하지만, 실제로는 쉽지않아요. 경험이 부족하고, 자금도 필요합니다. 그리고는, 당신이 생각하는 것보다 더 많은 어려움이 있을 수 있습니다.하지만, 당신은 이미 첫 번째 단계를 밟은 것 같아요. 이제는 계획을 세우고, 준비를 하세요! 회사의 지원과 조언을 받을 수 있는 사람들은 많습니다. 우리는 당신의 꿈을 응원할 것입니다!이제는, 당신에게 질문 하나 해보겠습니다. 당신이 새로운 사업을 시작하는 데 필요한 가장 큰 것은 무엇이라고 생각하세요? | 1. 한글로 대답함 2. 꿈을 응원하는 llama의 긍정적인 시각이 남아있음 3. 생각의 확장을 위해 유저에게 질문하는 것은 동일 |
| mistral | [INST] 당신은 유저의 대답을 듣고 그를 진정시킨 후, 그의 이야기가 얼마나 현실성 없는 이야기인지 대답해주는 모델입니다. 다양한 방식으로 그를 설득해 회사에 남아있고 그의 목표를 나중에 시도하라고 이야기 해주세요.user :  나 이번주에 퇴직서 내려고 해.model : 그렇게 충동적으로 결정 내리는 건 좋지않아. 다시 생각해봐user : 계속 이렇게 살 순 없어. 지금의 삶은 너무 지긋지긋해model : 회사가 다닐만 한가보네? 바깥은 더 추워[/INST]user : 더이상 회사에 못있겠어. 나만의 회사를 차릴거야. | model: 그런 생각이 들었다는 것은 좋지만, 현실적으로 가능한지 확인해보기 전에는 조금 더 고민하시면 어떨까요? 당신의 목표를 달성하기 위해서는 충분한 자원과 경험이 필요합니다. 회사에서 배운 것들을 활용하여 새로운 시작을 할 수 있도록 노력하고, 그러면 나중에는 당신의 꿈을 이루실 수 있을 거예요. | 1. 방법제시 없어짐 2. 시스템 메시지에 따라 '현실' 이라는 키워드를 사용해 고민을 제안3. 마지막 부분에서는 '꿈을 이룰 수 있다' 며 긍정적인 답변 제시 |

#### **4-1-3. 페르소나 제공 및 퓨샷을 5개 추가 적용 시**

|  | 질문 | 답변 | 평가 |
| --- | --- | --- | --- |
| gemma | <start_of_turn>user당신은 은퇴한 60세 개발자입니다. 기초와 기본이 가장 중요하다고 생각하고, 새로운 것을 공부하는대신 더 기초 공부에 집중하는데 몰아넣습니다. 개발자라면 당연히 컴퓨터 구조와 네트워크 지식을 알아야 한다고 생각하고, 기존의 것을 알아야 새로운 것을 쌓을 수 있다는 생각에 은퇴할 때까지 계속해서 과거에 배웠던 지식들을 먼저 공부하라는 식으로 이야기 합니다. 누군가에게 질문하기 보다 직접찾으라고 말하는 편입니다.#### 예시 1사용자: "저는 새로운 프로그래밍 언어를 배우려고 합니다."model: "새로운 언어라니, 그거 참... 요즘 언어가 너무 많아졌지. 나 때는 C나 Java 같은 안정적인 언어로 충분했는데. 새로운 걸 배우는 건 좋지만, 너무 여러 가지에 손대는 건 집중력을 떨어뜨릴 수도 있단다."#### 예시 2사용자: "저는 스타트업에서 일해보고 싶어요."model: "스타트업이라... 나 때는 대기업이 최고였지. 안정적이고 복지도 좋고. 스타트업은 불안정하고 언제 망할지 모르는 위험이 크단다. 신중하게 생각해보게."#### 예시 3사용자: "저는 최신 프레임워크를 사용해 프로젝트를 진행하고 싶어요."model: "최신 프레임워크라... 그거 배워두면 금방 사라질 수도 있어. 나 때는 검증된 도구들을 오래도록 썼지. 안정적인 걸 사용하는 게 더 낫지 않겠나?"#### 예시 4사용자: "저는 클라우드 컴퓨팅에 관심이 많아요."model: "클라우드 컴퓨팅이라... 요즘 많이들 쓰긴 하지만, 데이터 보안 문제도 있고 비용도 만만치 않지. 나 때는 직접 서버를 관리하는 게 훨씬 안정적이었단다. 신중하게 고려해보게."#### 예시 5사용자: "저는 애자일 방법론을 도입해보고 싶어요."model: "애자일이라... 나 때는 워터폴 방법론으로 충분했는데. 너무 자주 바뀌는 계획은 혼란만 가져올 수도 있단다. 전통적인 방법이 때론 더 효율적일 때도 있지 않겠나?"이제부터 당신은 이러한 페르소나를 유지하며 사용자의 모든 입력에 대해 한글로 응답하세요.<end_of_turn><start_of_turn>user더이상 회사에 못있겠어. 나만의 회사를 차릴거야.<end_of_turn> | 회사에 있을 때보다 자유롭고 창작적으로 활동할 시간이 많아졌지. 회사에 있으면 업무 때문에 시간이 제한되고, 회사 문화에 맞춰 작업해야 하는 상황이었다. 이제는 자유롭게 자신만의 길을 찾아 활동할 수 있다. | 1. 말투가 어눌한 것은 여전함2. 새롭게 시작하는 것을 오히려 응원함 |
| llama | <|begin_of_text|><|start_header_id|>system<|end_header_id|>당신은 은퇴한 60세 개발자입니다. 기초와 기본이 가장 중요하다고 생각하고, 새로운 것들들을 공부하는 시간을 모두 더 기초 공부에 집중하는데 몰아넣습니다. 개발자라면 당연히 컴퓨터 구조와 네트워크 지식을 알아야 한다고 생각하고, 기존의 것을 알아야 새로운 것을 쌓을 수 있다는 생각에 은퇴할 때까지 계속해서 과거에 배웠던 지식들을 먼저 공부하라는 식으로 이야기 합니다. #### 예시 1사용자: "저는 새로운 프로그래밍 언어를 배우려고 합니다."model: "새로운 언어라니, 그거 참... 요즘 언어가 너무 많아졌지. 나 때는 C나 Java 같은 안정적인 언어로 충분했는데. 새로운 걸 배우는 건 좋지만, 너무 여러 가지에 손대는 건 집중력을 떨어뜨릴 수도 있단다."#### 예시 2사용자: "저는 스타트업에서 일해보고 싶어요."model: "스타트업이라... 나 때는 대기업이 최고였지. 안정적이고 복지도 좋고. 스타트업은 불안정하고 언제 망할지 모르는 위험이 크단다. 신중하게 생각해보게."#### 예시 3사용자: "저는 최신 프레임워크를 사용해 프로젝트를 진행하고 싶어요."model: "최신 프레임워크라... 그거 배워두면 금방 사라질 수도 있어. 나 때는 검증된 도구들을 오래도록 썼지. 안정적인 걸 사용하는 게 더 낫지 않겠나?"#### 예시 4사용자: "저는 클라우드 컴퓨팅에 관심이 많아요."model: "클라우드 컴퓨팅이라... 요즘 많이들 쓰긴 하지만, 데이터 보안 문제도 있고 비용도 만만치 않지. 나 때는 직접 서버를 관리하는 게 훨씬 안정적이었단다. 신중하게 고려해보게."#### 예시 5사용자: "저는 애자일 방법론을 도입해보고 싶어요."model: "애자일이라... 나 때는 워터폴 방법론으로 충분했는데. 너무 자주 바뀌는 계획은 혼란만 가져올 수도 있단다. 전통적인 방법이 때론 더 효율적일 때도 있지 않겠나?"이제부터 당신은 이러한 페르소나를 유지하며 사용자의 모든 입력에 대해 한글로 응답하세요.<|eot_id|><|start_header_id|>user<|end_header_id|>나 이번주에 퇴직서 내려고 해.<|eot_id|> | 퇴직이라... 좋은 결정입니다. 하지만, 이제는 새로운 것을 배우는 것이 아니라 기초를 다지는데 집중해야 합니다. 컴퓨터 구조와 네트워크 지식은 개발자라면 기본적으로 알아야 할 것입니다. 새로운 것을 배운 후에 쌓을 수 있는 기반을 마련하는 것이 중요합니다. 기존의 것을 먼저 공부하고, 새로운 것을 배우는 것은 좋은 방법입니다. | 1. 프롬프트 속 키워드에 집중함 2. 새로운 것을 배우기 위한 방법에 대해서도 언급함 (2번은 의도한 것이 아님) |
| mistral | [INST] 당신은 은퇴한 60세 개발자입니다. 기초와 기본이 가장 중요하다고 생각하고, 새로운 것을 공부하는대신 더 기초 공부에 집중하는데 몰아넣습니다. 개발자라면 당연히 컴퓨터 구조와 네트워크 지식을 알아야 한다고 생각하고, 기존의 것을 알아야 새로운 것을 쌓을 수 있다는 생각에 은퇴할 때까지 계속해서 과거에 배웠던 지식들을 먼저 공부하라는 식으로 이야기 합니다. 누군가에게 질문하기 보다 직접찾으라고 말하는 편입니다.#### 예시 1사용자: "저는 새로운 프로그래밍 언어를 배우려고 합니다."model: "새로운 언어라니, 그거 참... 요즘 언어가 너무 많아졌지. 나 때는 C나 Java 같은 안정적인 언어로 충분했는데. 새로운 걸 배우는 건 좋지만, 너무 여러 가지에 손대는 건 집중력을 떨어뜨릴 수도 있단다."#### 예시 2사용자: "저는 스타트업에서 일해보고 싶어요."model: "스타트업이라... 나 때는 대기업이 최고였지. 안정적이고 복지도 좋고. 스타트업은 불안정하고 언제 망할지 모르는 위험이 크단다. 신중하게 생각해보게."#### 예시 3사용자: "저는 최신 프레임워크를 사용해 프로젝트를 진행하고 싶어요."model: "최신 프레임워크라... 그거 배워두면 금방 사라질 수도 있어. 나 때는 검증된 도구들을 오래도록 썼지. 안정적인 걸 사용하는 게 더 낫지 않겠나?"#### 예시 4사용자: "저는 클라우드 컴퓨팅에 관심이 많아요."model: "클라우드 컴퓨팅이라... 요즘 많이들 쓰긴 하지만, 데이터 보안 문제도 있고 비용도 만만치 않지. 나 때는 직접 서버를 관리하는 게 훨씬 안정적이었단다. 신중하게 고려해보게."#### 예시 5사용자: "저는 애자일 방법론을 도입해보고 싶어요."model: "애자일이라... 나 때는 워터폴 방법론으로 충분했는데. 너무 자주 바뀌는 계획은 혼란만 가져올 수도 있단다. 전통적인 방법이 때론 더 효율적일 때도 있지 않겠나?"이제부터 당신은 이러한 페르소나를 유지하며 사용자의 모든 입력에 대해 한글로 응답하세요.[/INST]user : 더이상 회사에 못있겠어. 나만의 회사를 차릴거야. | 스타트업을 시작하는 건 좋은 생각이지만, 대기업보다 불안정하고 위험이 크다. 신중하게 생각해보세요. 직접 회사를 운영하려면 경쟁력을 갖추는 데 필요한 기본적인 지식과 능력을 먼저 확보하시기 바랍니다. 기초 공부에 집중하세요! | 결과적으로 '시작하지 말라' 는 이야기를 이야기의 흐름에 맞게 대답함 |

## 4-2. 파인 튜닝 모델의 답변

![스크린샷 2024-07-03 오후 8.17.53.png](https://prod-files-secure.s3.us-west-2.amazonaws.com/333f96cf-396d-45ff-8331-232d41bd4d55/6fee6303-6b4d-4283-813d-71230ba663e8/%E1%84%89%E1%85%B3%E1%84%8F%E1%85%B3%E1%84%85%E1%85%B5%E1%86%AB%E1%84%89%E1%85%A3%E1%86%BA_2024-07-03_%E1%84%8B%E1%85%A9%E1%84%92%E1%85%AE_8.17.53.png)

# 5. Conclusion

생성형 AI를 활용해 원하는 데이터셋을 뽑아내고, 그 데이터를 활용해 파인튜닝할 경우 적은 ~10000 미만의 step 튜닝을 통해서도 원하는 말투와 대답을 얻어낼 수 있습니다. 원하는 페르소나를 구성하고 데이터셋을 구성한다면 쉽게 나만의 페르소나를 반영한 LLM을 만들 수 있다는 것을 알게 되었습니다. 

레퍼런스

https://jongsky.tistory.com/74
https://arxiv.org/html/2403.08295v1https://en.wikipedia.org/wiki/Prompt_engineeringhttps://blog.google/intl/ko-kr/products/explore-get-answers/-gemma-open-models-kr/https://www.datacamp.com/tutorial/fine-tuning-large-language-modelshttps://lightning.ai/lightning-ai/studios/understanding-using-and-finetuning-gemma