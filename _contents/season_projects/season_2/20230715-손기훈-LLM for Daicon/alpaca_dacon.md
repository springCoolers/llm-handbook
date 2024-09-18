# CausalLM for parameter tuning and classification(feat. ALpaca, Dacon)

## Causal LM

### what is causal langauge model?

- GPT, llama, Alpaca, palm …etc

![llm_paint.png](./asstes/llm_paing.png)

- 이전의 입력 토큰을 통해 다음 토큰을 생성하는 자기회귀적 모델이다. 이전의 문맥을 반영하여 입력에 대한 출력을 내놓기 때문에 Causal LanguageModel로 불린다.

### Prompt Tuning

프롬프트 튜닝은 파인튜닝의 한 갈래로서, auto regressive 한 모델에 인풋데이터에 특정한 인스터럭션을 주어 원하는 답변을 생성하게 하는 태스크이다. 

- Alpaca Finetuning
    - Alpaca-7b 모델을 파인 튜닝하는 것 자체는 사실 어려운 태스크가 아니었고, 코드 한 줄로도 가능한 일이었다.
    - 아래의 포맷에 맞추어 json형태로 데이터를 저장하고 불러와 튜닝을 시키면 되었다.
        
        ```python
        ### 파인 튜닝 시 프롬프트 포맷
        
        def generate_prompt(data_point):
            return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.  # noqa: E501
        ### Instruction:
        {data_point["instruction"]}
        ### Input:
        {data_point["input"]}
        ### Response:
        {data_point["output"]}"""
        
        ### inference 시의 프롬프트 포맷
        
        def create_prompt(data_point):
            return f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.  # noqa: E501
        ### Instruction:
        {data_point["instruction"]}
        ### Input:
        {data_point["input"]}
        ### Response:
        """
        
        ### inference 답변 생성 함수들
        
        def generate_response(prompt: str, model: model):
            encoding = tokenizer(prompt, return_tensors="pt")
            input_ids = encoding["input_ids"].to(DEVICE)
         
            generation_config = GenerationConfig(
                temperature=0.1,
                top_p=0.75,
                repetition_penalty=1.1,
            )
            with torch.inference_mode():
                return model.generate(
                    input_ids=input_ids,
                    generation_config=generation_config,
                    return_dict_in_generate=True,
                    output_scores=True,
                    max_new_tokens=1,
                )
        
        def format_response(response) -> str:
            decoded_output = tokenizer.decode(response.sequences[0]) 
            response = decoded_output.split("### Response:")[1].strip()
            return "\n".join(textwrap.wrap(response))
        
        def ask_alpaca(prompt, model: model) -> str:
            prompt = create_prompt(prompt)
            response = generate_response(prompt, model) # 굉장히 많은 답변이 생성됨
            response = format_response(response)
            return response
        
        ### 
        ```
        
- Loss Function of Auto Regressive Model - 여담
    - 생성 모델의 loss function은 어떻게 굴러가는지 궁금해서 한번 찾아봄
    
    ```python
    ## huggning face에 nlp course에 있는 코드
    
    from torch.nn import CrossEntropyLoss
    import torch
    
    def keytoken_weighted_loss(inputs, logits, keytoken_ids, alpha=1.0):
        # Shift so that tokens < n predict n
        shift_labels = inputs[..., 1:].contiguous()
        shift_logits = logits[..., :-1, :].contiguous()
        # Calculate per-token loss
        loss_fct = CrossEntropyLoss(reduce=False)
        loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
        # Resize and average loss per sample
        loss_per_sample = loss.view(shift_logits.size(0), shift_logits.size(1)).mean(axis=1)
        # Calculate and scale weighting
        weights = torch.stack([(inputs == kt).float() for kt in keytoken_ids]).sum(
            axis=[0, 2]
        )
        weights = alpha * (1.0 + weights)
        # Calculate weighted average
        weighted_loss = (loss_per_sample * weights).mean()
        return weighted_loss
    ```
    
    - Token_1 의 타겟은 Token_2 이다.
    - 따라서 타겟 토큰은 2번째부터 마지막까지, 입력 토큰은 1번째부터 마지막 이전 토큰까지.
    - 각 loss를 계산해준 이후에는, 등장 빈도를 가중치로 사용하여 모든 샘플에 대한 가중 평균을 계산해준다.

### p-tunig for classification

- hugging face 의 peft의 예시
    
    ```python
    peft_config = PromptTuningConfig(
        task_type=TaskType.CAUSAL_LM,
        prompt_tuning_init=PromptTuningInit.TEXT,
        num_virtual_tokens=8,
        prompt_tuning_init_text="Classify if the tweet is a complaint or not:", ## 인스트럭션을 따로 줄 수 있다.
        tokenizer_name_or_path=model_name_or_path,
    )
    
    ...
    
    f'{text_column} : {"@nationalgridus I have no water and the bill is current and paid. Can you do something about this?"} Label : ',
    ```
    
- Alpaca의 예시 - 위 참고

# Dacon에 적용

### 배경

- 원고의 승소 여부를 물어보는 과제였으므로, 단순한 classification 보다 복잡한 문제라고 생각했다.
- 이 문제를 alpaca에 prompt-tuning으로 접근하여 해결 가능한 문제라고 생각함.

### 데이터 탐색 및 전처리

1. 데이터 길이 탐색
    - train length
    
    ![Untitled](CausalLM%20for%20parameter%20tuning%20and%20classification(f%20bfd645a65c9c442e9a3d1be2a7f987b1/Untitled.png)
    
    - test length
    
    ![Untitled](CausalLM%20for%20parameter%20tuning%20and%20classification(f%20bfd645a65c9c442e9a3d1be2a7f987b1/Untitled%201.png)
    
2. 라벨 탐색
    
    ![Untitled](CausalLM%20for%20parameter%20tuning%20and%20classification(f%20bfd645a65c9c442e9a3d1be2a7f987b1/Untitled%202.png)
    
3. ner 태그 탐색
    - first_party
    
    ![Untitled](CausalLM%20for%20parameter%20tuning%20and%20classification(f%20bfd645a65c9c442e9a3d1be2a7f987b1/Untitled%203.png)
    
    - second_party
    
    ![Untitled](CausalLM%20for%20parameter%20tuning%20and%20classification(f%20bfd645a65c9c442e9a3d1be2a7f987b1/Untitled%204.png)
    
    - first_party, second_party의 ner을 탐색하여 인명, 지명, 조직 등등에 맞추어 룰 베이스로 처리하여 facts 안에 등장하는지 여부를 찾고자 함
        1. full name이 이미 facts안에 있는 경우
            - 이 경우엔 ner 상관 없이 바로 prompt를 생성 가능하므로 따로 빼어 관리
            - 1550 개의 row
        2. full_name이 facts안에 없는 경우
            
            ner을 적용한 후에, ner 태그가 하나만 있는 데이터들을 모아서 처리
            
            - PER 태그 : 간단한 클렌징 이후에 first_name과 last_name이 있는지를 체크하였다.
            - ORG, LOC, MISC : 간단한 클렌징 이후에 n-gram을 적용하여 facts안에 있는지 여부를 체크하였다.
            - 498 row
        3. full_name이 facts안에 없고 ner tag가 여러개인 경우
            - 이 경우에는 2번의 경우보다 일반적으로 처리해야 했으므로 n-gram을 적용하여 facts안에 있는지 여부를 체크하였다.
            - 430 rows
4. 프롬프트 생성
    - 만약 first_party가 있으면, f“Does {first_party} win” 의 프롬프트를 넣어주고, second_party가 있으면 f”Does {second_party} win”을 넣어줌, 둘 다 없는 경우는 “Does Complainant win?” 프롬프트를 넣어주었다.
    - 답변
        - ‘yes’
            - first_party와 first_party_winner 가 같은 라벨 1==1, 0==0인 경우와 프롬프트에 ‘Complainant’가 등장하고, first_party_winner가 1인 경우
        - ‘no’
            - first_party가 0이고 first_party_winner가 1인 경우에는 ‘No”, first_party가 1이고 first_party_winner가 0인 경우, ‘Complainant’가 등장하고 first_party_winner가 0인 경우
        

### Reference

- Hugging Face

[인과 언어 모델링](https://huggingface.co/docs/transformers/v4.30.0/ko/tasks/language_modeling)

[Prompt tuning for causal language modeling](https://huggingface.co/docs/peft/task_guides/clm-prompt-tuning)

- github

[https://github.com/kairess/alpaca-lora](https://github.com/kairess/alpaca-lora)

[https://github.com/Beomi/KoAlpaca](https://github.com/Beomi/KoAlpaca)

- blog

[Fine-tuning Alpaca and LLaMA: Training on a Custom Dataset | MLExpert - Crush Your Machine Learning interview](https://www.mlexpert.io/machine-learning/tutorials/alpaca-fine-tuning)

[Alpaca and LLaMA: Inference and Evaluation | MLExpert - Crush Your Machine Learning interview](https://www.mlexpert.io/machine-learning/tutorials/alpaca-and-llama-inference)
