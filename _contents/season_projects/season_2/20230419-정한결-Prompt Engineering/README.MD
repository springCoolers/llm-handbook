## Prompt Engineering

---

https://www.youtube.com/watch?v=Qos2rG3zVAM

Level 0: what is good diet to lose weight 

Level 1: I want to lose 11 pounds in next 60 days. can you help me? 

→ 측정가능하고 액션어블한 **Goal**이 있다. 

Level 2: Here are some contexts for my weight loss plans: I am 40 year old man, i weigh 213 pounds (97kg) now, in the next 60 days i want to lose weight so i am under 200 pounds (90kg). I do some cardio, i try to walk 20 minutes each day, but i also think i eat a bit too much. I don’t want diet that is too hard to follow. I am also willing to exercise more. Can you write a diet plan for the next 8 weeks for me? 

→ Context가 추가됨. 현재 몸무게, 더 운동하고 싶음, 

Level 3: 

#1 You are a weight loss and diet expert. Your task is to help the USER find a diet and strategy that fits the needs and goals, you will create a detailed, easy to follow diet and exercise plan for user. Also make an accountability plan. Be very helpful and motivating. Acknowledge this by answering yes and staying idle. 

#2 Here are some context i found in my research : [연구자료] 

confimr you read this by answering yes and staying idle. 

#3 Here are my context for weight loss goals… [level 2 반복] 

→ Role and Persona

→ 프롬프트를 통해 문서를 입력하여 파인튜닝 (이라고 해도 되나?) 

→ 이후 Goals, Context를 입력 

- 추가적인 기능 : audio 생성, 비디오 인식 등 multimodal한 것들을 붙여서, 최종적으로 답안을 텍스트 이외의 형태로 리턴하게 하셨음.

### Introduction

---

- Prompt Elements
    
    **Instruction** - a specific task or instruction you want the model to perform
    
    **Context** - can involve external information or additional context that can steer the model to better responses
    
    **Input Data** - is the input or question that we are interested to find a response for
    
    **Output Indicator** - indicates the type or format of the output.
    

## General Tips

---

1. Simple하게 시작하고, 반복적으로 업그레이드 하자 Iterative 
    1. Versioning your prompt along the way is vital for this reason.
2. The Instruction (=Goal)
    1. 여러 가지 단어로 실험해 볼 것. 
        1. "Write", "Classify", "Summarize", "Translate", "Order”
    2. Others recommend that instructions are placed at the beginning of the prompt. 
    3. It's also recommended that some clear separator like "###" is used to separate the instruction and context.
    
    ```solidity
    ### Instruction ###
    Translate the text below to Spanish:
    Text: "hello!"
    
    output: 
    
    ¡Hola!
    ```
    
3. Context / System level Instruction의 Specificity ↔ Openness 
    1. The more descriptive and detailed the prompt is, the better the results. 
        1. 사용자가 원하는게 구체적일수록, 더 구체적인 요구를 할 것. 
            1. 의학, 법 문서 생성 VS  브레인스토밍, 소설 쓰기
        2. Tradeoff : 구체적으로 주문할 수록 모델의 창의성이 제한됨. 
            1. 모델보고 prompt를 suggest 하라는것도 방법일 듯 
        3. Tradeoff 2: 토큰 수 제한. 
    2. Providing examples in the prompt is very effective to get desired output in specific formats. (→ Few shot) 
        
        ```solidity
        
        # Input
        
        Extract the name of places in the following text. 
        Desired format:
        Place: <comma_separated_list_of_company_names>
        Input: "Although these developments are encouraging 
        to researchers, much is still a mystery. 
        “We often have a black box between the brain 
        and the effect we see in the periphery,” 
        says Henrique Veiga-Fernandes, a neuroimmunologist at the Champalimaud Centre for the Unknown in Lisbon. “If we want to use it in the therapeutic context, we actually need to understand the mechanism.""
        
        #Output: 
        
        Place: Champalimaud Centre for the Unknown, Lisbon
        ```
        
    3. System Level instruction에 해당하는 것들 
        1. Output length 
            1. “max_tokens” “min_tokens” 등 파라미터 형태로 제한도 가능함. (api 호출시겠죠?) 
        2. format
        3. personality
        4. diversity / creativity - temp와 top_p 파라미터를 통해 조절가능함. 
            - LLM Settings
                
                Greedy Search - 매 단계 가장 확률이 높은 결과를 채택하나, 그렇기에 반복적이거나 다양성이 부족한 답변들이 나올 가능성이 높다 
                
                Beam Search - 그리디를 넘어서 여러 가설을 보존하지만(?) 여전히 다양성이 부족해질 수 있음. 
                
                **Temperature** - In short, the lower the `temperature`, the more deterministic the results in the sense that the highest probable next token is always picked. Increasing temperature could lead to more randomness, which encourages more diverse or creative outputs. You are essentially increasing the weights of the other possible tokens. In terms of application, you might want to use a lower temperature value for tasks like fact-based QA to encourage more factual and concise responses. For poem generation or other creative tasks, it might be beneficial to increase the temperature value.
                
                **Top_p** - Similarly, with `top_p`, a sampling technique with temperature called nucleus sampling, you can control how deterministic the model is at generating a response. If you are looking for exact and factual answers keep this low. If you are looking for more diverse responses, increase to a higher value.
                
4. ****Avoid Impreciseness****
    
    ```python
    #Bad example:how many sentences to use and what style
    Explain the concept prompt engineering. Keep the explanation short, only a few sentences, and don't be too descriptive.
    
    Use 2-3 sentences to explain the concept of prompt engineering to a high school student.
    ```
    
5. ****To do or not to do?****
    
    Another common tip when designing prompts is to avoid saying what not to do but say what to do instead. This encourages more specificity and focuses on the details that lead to good responses from the model.
    
    Here is an example of a movie recommendation chatbot failing at exactly what I don't want it to do because of how I wrote the instruction -- focusing on what not to do.
    
    *Prompt:*
    
    ```
    The following is an agent that recommends movies to a customer. DO NOT ASK FOR INTERESTS. DO NOT ASK FOR PERSONAL INFORMATION.Customer: Please recommend a movie based on my interests.Agent:
    ```
    
    *Output:*
    
    ```
    Sure, I can recommend a movie based on your interests. What kind of movie would you like to watch? Do you prefer action, comedy, romance, or something else?
    ```
    
    Here is a better prompt:
    
    *Prompt:*
    
    ```
    The following is an agent that recommends movies to a customer. The agent is responsible to recommend a movie from the top global trending movies. It should refrain from asking users for their preferences and avoid asking for personal information. If the agent doesn't have a movie to recommend, it should respond "Sorry, couldn't find a movie to recommend today.".Customer: Please recommend a movie based on my interests.Agent:
    ```
    
    *Output:*
    
    **`Sorry, I don't have any information about your interests. However, here's a list of the top global trending movies right now: [list of movies]. I hope you find something you like!`**
    

### Techniques

---

**[Zero-shot Prompting](https://www.promptingguide.ai/techniques/zeroshot)** 

[Few-shot Prompting](https://www.promptingguide.ai/techniques/fewshot)

[Chain-of-Thought Prompting](https://www.promptingguide.ai/techniques/cot)

[Self-Consistency](https://www.promptingguide.ai/techniques/consistency)

[Generate Knowledge Prompting](https://www.promptingguide.ai/techniques/knowledge)

[Automatic Prompt Engineer](https://www.promptingguide.ai/techniques/ape)

[Active-Prompt](https://www.promptingguide.ai/techniques/activeprompt)

[Directional Stimulus Prompting](https://www.promptingguide.ai/techniques/dsp)

[ReAct](https://www.promptingguide.ai/techniques/react)

[Multimodal CoT](https://www.promptingguide.ai/techniques/multimodalcot)

[Graph Prompting](https://www.promptingguide.ai/techniques/graph)

**Mastering GPT-4: A Comprehensive Prompt Engineering Guide**

[20-Effective-ChatGPT-Prompts.pdf](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/ed2f9610-a04a-45a8-8cf9-2842fabde5b3/20-Effective-ChatGPT-Prompts.pdf)

이 자체로 논문 Heavy한 친구들 

### Prompt Engineering (조금) 적용하기

---

### Hypothesis:

→ 생성 모델의 Tokenizer에 OOV로 뜨면, 그건 신조어일 가능성이 크다 

### 결과:

Q : You are Large Language Model. In the text below, list newly coined words. If a word is considered Out of Vocabulary in tokenizer you use, it is newly coined word. 

Spring is here, the NFT100 is a month away, and Ethereum Co-Founder Vitalik Buterin just made a huge announcement: Soulbound Tokens (SBTs). The idea — which came via a white paper entitled “Decentralized Society: Finding Web3’s Soul” — inspires “oohs” and “ahhs” throughout the metaverse. That same month, the paper’s co-author E. Glen Weyl states that early uses of SBTs may be available by the end of 2022.

Yet, fast forward to January 2023, and where are all these early use-case SBTs to be found? Did the NFT space glaze over this potentially paradigm-shifting technology in favor of more Bored Ape derivatives… again? Or is there simply a lack of infrastructure to create SBTs in the first place? Maybe both, or maybe neither — because SBTs are here, but they are still far from their final form.

A : NFT100, Vitalik Buterin, Soulbound Tokens (SBTs), Decentralized Society: Finding Web3’s Soul, metaverse, E. Glen Weyl, Bored Ape derivatives.

Q: Print the attention scores of previous word list

A: As an AI language model, I don't have the ability to print attention scores for a word list. Attention scores are generated during the language model's training and are not directly accessible outside of the model's internal workings. However, I can generate text with attention scores highlighted to give you an idea of how the model pays attention to certain words in a given context. Let me know if you'd like me to generate such text.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/a4f2e7f8-7f54-4ab3-b1e2-9595e56e2c9e/Untitled.png)

<aside>
💡 발견:  Attention Score에는 접근이 불가능하다!

</aside>

### bingchat으로 하면 어떨까?

---

같은 질문을 Bingchat에 던졌다. 

Q: You are Large Language Model. Your role is to find and list newly coined words in given text. If a word is considered Out of Vocabulary in tokenizer you use, it is newly coined word. Say yes if you understood.

A: Yes, I understand what you are asking for. However, I must clarify that I cannot list newly coined words that are considered Out of Vocabulary in the tokenizer I use because I do not have access to the tokenizer’s vocabulary. Therefore, I can only list newly coined words that are not Out of Vocabulary in the tokenizer I use.

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/adc4caec-99a4-4671-8d97-8b6aaa1125ee/Untitled.png)

<aside>
💡 bingchat은 tokenizer에 접근이 안된다고 한다 (!)

</aside>

가설 2: 검색엔진에게, 특정 시점을 넣어달라고 했다. 

Q: Your role is to find and list newly coined words in given text. If a word or phrase has first emerged in your search engine after January 2022, it is considered a newly coined word. Say yes if you understood.

A: Yes, I understand what you are asking for. I will list newly coined words or phrases that have first emerged in my search engine after January 2022.

Q: Spring is here, the NFT100 is a month away, and Ethereum Co-Founder Vitalik Buterin just made a huge announcement: Soulbound Tokens (SBTs). The idea — which came via a white paper entitled “Decentralized Society: Finding Web3’s Soul” — inspires “oohs” and “ahhs” throughout the metaverse. That same month, the paper’s co-author E. Glen Weyl states that early uses of SBTs may be available by the end of 2022. Yet, fast forward to January 2023, and where are all these early use-case SBTs to be found? Did the NFT space glaze over this potentially paradigm-shifting technology in favor of more Bored Ape derivatives… again? Or is there simply a lack of infrastructure to create SBTs in the first place? Maybe both, or maybe neither — because SBTs are here, but they are still far from their final form.

A: In the given text, the newly coined word or phrase that has first emerged in my search engine after January 2022 is “Soulbound Tokens (SBTs)” which was proposed in May 2022 in a whitepaper entitled “Decentralized Society: Finding Web3’s Soul,” by economist & social technologist E. [Glen Weyl, lawyer Puja Ohlhaver, and Ethereum creator Vitalik Buterin**1](https://dev.to/envoy_/what-are-soulbound-tokens-14lj)[2](https://nftnow.com/features/nfts-2-0-when-will-soulbound-tokens-arrive/):**

 ****

### 오늘의 발견:

Newly Coined word Detector에 사용할 수 있다 

model 1 - GPT3의 Tokenizer에게 물어본다

model 2 - Bing Chat에 일정 시점 이후에 등장한/trending 단어들을 모으라고 해라 

### To-do list

- [ ]  Prompt Engineering 관련 논문들을 찾고 정리해야겠다.
    - [읽을 자료 확장](https://www.emergentmind.com/?before=2023-04-15)하기 : EmergentMind / [allabtai](https://www.allabtai.com/prompt-engineering/)
    - 어플리케이션 팔로업: [ChatGLM](https://www.youtube.com/watch?v=fGpXj4bl5LI) / Langchain / AutoGPT
- [ ]  Prep Test Dataset
- [ ]  Prompt Template Iibrary를 생성해야 할 필요가 있다.
- [ ]  “Instruction”의 종류가 궁금하다. 무한하진 않을 거 아냐
    - [ ]  "Write", "Classify", "Summarize", "Translate", "Order”
- [ ]  성능 지표 정하기. FP / Bleu, rouge, meteor
- [ ]  단어 자체는 이미 있는데, 다른 뜻으로 trending한 경우를 찾아낼 수 있을까? 어떻게?
- [ ]  프롬프트를 이해하는 방법이 궁금하다! Openprompt 외에 논문 뭐가 있지

# IDEAS : what other people do

---

- **[The ChatGPT Startup Bible: Your Guide to Building and Growing Your Business with AI](https://www.amazon.com/dp/B0C1J3DCRQ/ref=sspa_dk_detail_3?psc=1&pd_rd_i=B0C1J3DCRQ&pd_rd_w=DzfR0&content-id=amzn1.sym.ecc09a2f-2609-4555-bb4e-a89772637d1c&pf_rd_p=ecc09a2f-2609-4555-bb4e-a89772637d1c&pf_rd_r=4NRCX4PH862HX9117AH9&pd_rd_wg=dCzCg&pd_rd_r=8f265312-abaa-4dac-8716-351412997216&s=books&sp_csd=d2lkZ2V0TmFtZT1zcF9kZXRhaWxfdGhlbWF0aWM&spLa=ZW5jcnlwdGVkUXVhbGlmaWVyPUEyVkI2REVMQ0lWSVhBJmVuY3J5cHRlZElkPUEwMTkxNjc1MVNJTUg3WUI5MVgzUCZlbmNyeXB0ZWRBZElkPUEwNjA2NjM3M0VXM01ZVjRXRUJPNCZ3aWRnZXROYW1lPXNwX2RldGFpbF90aGVtYXRpYyZhY3Rpb249Y2xpY2tSZWRpcmVjdCZkb05vdExvZ0NsaWNrPXRydWU=)**

