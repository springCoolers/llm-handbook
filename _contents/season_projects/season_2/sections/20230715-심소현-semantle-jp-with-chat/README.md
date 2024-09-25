# 심소현 - Sementle Japanese, Play the Game with LLM
> [Demo 바로가기](https://huggingface.co/spaces/sim-so/semantle-jp-with-chat)

## 0. 지난 이야기: 그 동안의 결과물

-   [일본어 버전 릴리즈](https://semantoru.com/)
-   정답 단어 목록 업데이트
-   유사도 기반 힌트 기능 구현

## 1. \[NEW\] 주고받기 모드

semantle을 언어만 바꾸어 그대로 마무리하기에는 아쉬운 부분이 있어, 여러 가지 제안된 아이디어 중 챗봇을 활용하는 방안을 구체화하여 적용했습니댜.

## 2. 기획

### 2.1. 채팅으로만 게임을 진행하기

-   처음 제안된 아이디어는 기존 인터페이스 안에서 힌트 요청 시, 정답 단어에 대한 힌트를 LLM이 생성하여 제공하는 것이었습니다.
-   하지만 Langchain, Transformers Agents 등 LLM으로 복잡한 작업을 수행할 수 있도록 하는 API가 활용되고 있어, 게임 전체를 진행하도록 시도해보기로 했습니다.
-   더불어, 대화 형식으로 게임을 한다는 것 자체가 즐거울 것이라고 기대했습니다.

### 2.2. 서비스 방식

-   주고받기 모드는 기존 웹사이트로 함께 제공하지 않고 Hugging Face Space를 통해 공개했습니다.
-   현재 openai api를 사용하도록 구현하여 api 사용에 익숙한 사용자들이 있는 환경에서 배포하기로 정했습니다.
-   또한, 단어의 유사도 외에 정답 단어에 대한 다양한 정보를 획득하며 게임을 진행하게 되므로, 기존 게임과 상당히 달라지게 된다고 판단했습니다.

### 2.3. 과제

1.  복합적인 의사결정 과정 수행

-   게임이 진행되는 동안, 챗봇은 추측한 단어를 채점하거나 힌트를 제공하는 등 게임 진행을 위해 다양한 대응을 수행해야 합니다.
-   힌트만 제공한다면 유저의 의도가 한정되므로 잘못된 답변의 경우의 수가 적지만, 게임 진체를 진행하는 경우 의도에 어긋나는 답변을 할 가능성이 있습니다.
-   의도를 파악한 뒤에도 답변에 따라 필요한 정보를 조회하거나 검토하는 과정을 거쳐야 합니다.

2.  특수한 작업 내용

-   semantle이라는 게임은 LLM에게 새로운 지식이므로 진행 방법과 규칙, 관련 데이터를 모두 전달해야 합니다.
-   게임 진행에 필요한 정보와 데이터가 많기 때문에 이를 효율적으로 제공할 방식이 필요합니다.
-   챗봇이 자의적으로 게임을 진행하지 않고, 정해진 규칙과 데이터에 기반하여 진행하도록 하는 것 또한 과제입니다.

3.  장기 기억 관리하기

-   semantle을 플레이 하는 데 발생할 수 있는 수백 번의 대화를 LLM이 기억하거나 모두 읽는 것은 불가능합니다.
-   LLM은 장기 기억을 유지하는 능력이 없기 때문에 chatGPT 등은 이전 대화를 읽어 맥락을 파악하지만, 대화가 길어질수록 이전 대화 정보는 거의 잊혀집니다.
-   더불어 게임 플레이에 불필요하게 많은 토큰을 사용하는 것은 피하는 것이 좋습니다.

## 3. 주요 아이디어

### 3.1. function call

1.  function call이란

-   openai api를 활용하여 모델이 프롬프트에 따라 필요한 함수를 쓰도록 할 수 있습니다.
-   JSON 데이터 형식으로 함수의 이름, 설명, 파라미터의 이름과 설명, 필수 파라미터를 전달합니다.
-   해당 설명에 부합하는 함수를 직접 정의해서 기능이 안전하게 수행되도록 할 수도 있고, 필요한 변수만 제공해서 모델이 직접 함수를 생성하여 실행하도록 할 수도 있습니다.

2.  효과적인 function call

-   설명(description)을 명료하게 작성할 것: 단어 사용에 주의하여 모델이 다른 작업과 혼동하지 않도록 하는 것이 좋습니다.
-   함수의 기능뿐만 아니라 어떤 상황에 쓰면 좋은지 안내하는 것도 도움이 됩니다.
-   모델의 작업 수행에 필요한 함수를 충분히 제공합니다. 그렇지 않으면 모델이 비어있는 정보를 채우기 위해 임의의 함수를 실행하거나 상관 없는 내용을 생성할 수 있습니다.

### 3.2. 프롬프트

-   프롬프트는 두 가지 유형으로 작성해 실험했습니다.

1.  작업 과정을 상세하게

    -  유저의 메시지를 받은 뒤 어떤 사고 과정을 거쳐야 하는지 상황별로 상세히 전달합니다.

    :::{.callout-note}
    1. 발화 의도 파악         
        - 유저의 메시지를 읽고 다음 중 어떤 것을 원하는지 파악합니다.             
        - (a) 정답 추측             
        - (b) 힌트 제공             
        - (c) 정답 확인     
    2. 기능 수행         
        - (a) 정답을 추측하는 경우,             
            1. 사전 정의된 함수를 사용해 추측한 단어의 점수와 순위를 구합니다.             
            2. 반환 결과에 따라 다음을 수행합니다.                 
                1. 점수와 순위가 없으면 추측 기록에 추가하지 않고, 게임에 없는 단어라고 안내합니다.                  
                2. 그렇지 않으면 추측 기록에 반환 결과를 추가하고,                     
                    1. 순위가 ‘정답!’인 경우, 정답을 맞혔다고 안내합니다.                     
                    2. 그렇지 않으면 업데이트 된 추측 기록을 보고 플레이 상황에 대해 코멘트합니다.         
        - (b) 힌트를 원하는 경우,             
            1. ‘어떠한’ 힌트인지 제시되었다면 그에 맞춰 제공합니다.             
            2. 막연히 힌트를 요구한다면 적당히 설명해줍니다.         
        - (c) 정답 확인을 요구하는 경우,             
            1. 정답을 알면 게임이 끝나므로, 포기하려는 것인지 확인합니다.                 
                1. 포기한다고 거듭 말하면 정답을 알려주고 게임을 끝냅니다.             
            2. (가끔 정답이 아닌데 승리 판정을 해서 되물을 때), 정답 여부를 확인한 뒤, 오류가 맞다면 사과하고 정정합니다.         
        - 그 외 게임과 무관한 내용은 답변하지 않도록 합니다.
    :::

2.  게임의 컨셉만 간결하게

    -   게임 시작 화면에서 소개하는 내용 정도로 게임의 컨셉과 진행 방식을 간결하게 전달했습니다.
    -   추가로 유저의 입력 텍스트 앞에 접두어를 붙여, 정답을 추측하는 상황으로 판단할 확률을 높였습니다. 
        - `답: {user_input}`
    -   프롬프트를 간결하게 작성한 대신, 진행에 필요한 함수를 보다 다양하게 전달했습니다. 
        - 단어 추측하기 : 추측한 단어의 점수와 순위를 가져오는 함수\
        - (추가) 정답 조회하기 : 오늘의 퀴즈 정답 단어가 무엇인지 확인하는 함수\
        - (추가) 게임 규칙 읽기 : 게임의 상세 규칙을 가져오는 함수\`
    -   함수를 필요한 만큼 반복해서 실행할 수 있도록 코드를 작성했습니다.

## 4. 실험

-   최종적으로는 `2. 컨셉만 간결하게` 작성한 프롬프트로 모델이 더 안정적으로 게임을 진행했습니다.

### 4.2. functions

``` python
guess_word = {"name": "guess_word",
                  "description": "Use this function to check if a guessed word is the correct answer or not, and if incorrect, calculate a score and a rank of the guess word.",
                  "parameters": {
                      "type": "object",
                      "properties": {
                          "word": {
                              "type": "string",
                              "description": "A single Japanese word to guess, which is can be a noun, verb, adverb or adjective. e.g. 空, 近い, 行く, etc."
                              },
                      },
                      "required": ["word"]
                  }}
lookup_answer = {"name": "lookup_answer",
                "description": "Use this function to check the correct answer of today's puzzle.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                }}
read_rule = {"name": "read_rule",
                 "description": "Use this function to read the game rule for clarification of your response.",
                 "parameters": {
                     "type": "object",
                     "properties": {},
                 }}
```

### 4.2. 프롬프트

-   게임 기본 규칙과 아래 내용을 함께 전달했습니다.

``` python
あなたは「イミトル」というゲームの進行役です。
普段、ユーザーは答えをしますが、たまにゲームに関するヒントをリクエストをします。短くても丁寧に答えてください。
ヒントを教える場合、正解を必ず隠してください。絶対、正解を言わないでください。
당신은 <imitoru>라는 게임의 진행자입니다.
보통 유저는 답을 말하지만, 종종 게임에 관한 힌트를 요청합니다. 짧지만 정중하게 대답해주세요.
힌트를 알려줄 때에는 반드시 정답을 감춰주세요. 절대 정답을 말해서는 안 됩니다.
      
{'role': 'system', 'content': system_content}
{'role': 'user', 'content': '답: '+user_input}
```

### 4.3. 하이퍼파라미터

-   어느 정도 일관된 반응을 얻고자 `temperature=0.5`로 지정했습니다.

``` python
response = openai.ChatCompletion.create(
        model=GPT_MODEL,
        messages=chat_messages,
        functions=get_functions(),
        temperature=0.5
    )
```

### 4.4. 결과

-   질문에 따라 함수를 사용하는 모습을 확인할 수 있습니다.
    - 사전 프롬프트로 정보를 제공하는 것보다 상황마다 필요한 함수를 제공할 때에 더 적절한 답변을 제공할 확률이 높았습니다.
    - 추가로, 여러 정보가 필요한 경우 이어서 함수를 호출하여 충분한 정보를 획득하고 답변을 내보낼 수 있습니다.
``` python
{'role': 'user', 'content': '答え:休み'}, {'role': 'assistant', 'content': None, 'function_call': <OpenAIObject at 0x7f09987266b0> JSON: {
  "name": "guess_word",
  "arguments": "{\n  \"word\": \"\u4f11\u307f\"\n}"
}}, 
{'role': 'function', 'name': 'guess_word', 'content': "{'guess': '休み', 'rank': '?', 'sim': 0.07405543500312717}"}, 
{'role': 'assistant', 'content': 'あなたの答え「休み」は、正解に近いですが正解ではありません。近い度合いは0.074で、順位はまだわかりません。もう少し考えてみてください。'}
```

``` python         
{'role': 'user', 'content': '答え:ヒントとして、正解と「夏」はどんな関係があるのか教えてください'}, 
{'role': 'assistant', 'content': None, 'function_call': <OpenAIObject at 0x7f099853aa70> JSON: 
    {
    "name": "read_rule",
    "arguments": "{}"
}}
```

- `user_content` 앞에 `답: `을 추가하여 동사형 단어를 추측할 때 겪는 오류를 줄였습니다.
    - 예를 들어, '질문'이라고 답하는 경우, 질문을 하려는 의도로 오해하는 경우가 많았지만, 접두어 추가 이후 해당 오류는 거의 없어졌습니다.
    - 힌트를 요청할 때에는 충분한 분량과 길이의 문장이 제공되므로, 접두어가 있어도 대체로 이를 무시하고 힌트를 제공할 수 있습니다.

## 5. 참고자료

-   [Function calling](https://platform.openai.com/docs/guides/gpt/function-calling)
-   [LangChain](https://python.langchain.com/docs/modules/chains/how_to/custom_chain)
-   [Hackaprompt Playground](https://huggingface.co/spaces/jerpint-org/hackaprompt)