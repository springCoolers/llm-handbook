# 메모리(Memory) in LLM

## 요약
메모리(Memory) in LLM은 대형 언어 모델(Large Language Model, LLM)이 과거의 상호작용을 기억하고 참조할 수 있는 능력을 말합니다. 이 기능은 대화 AI 시스템에서 매우 중요하며, 사용자와의 상호작용을 더 자연스럽고 효과적으로 만듭니다. 메모리는 LLM이 이전의 대화를 기억하고, 새로운 질의에 대한 응답을 생성할 때 이전의 정보를 사용할 수 있도록 합니다. 이 기능은 LangChain과 같은 프레임워크를 사용하여 구현할 수 있으며, 다양한 메모리 유형과 구현 방법이 있습니다.

## 핵심 개념
- **메모리(Memory)** : LLM이 과거의 상호작용을 기억하고 참조할 수 있는 능력.
- **메모리 구현 방법** : LangChain을 사용하여 대화 버퍼 메모리, 대화 요약 메모리 등 다양한 메모리 유형을 구현할 수 있습니다.
- **메모리 소스** : 메모리 내용이 어디서 오는지에 대한 정보. 예를 들어, 사용자 입력이나 이전 대화 기록.
- **메모리 형식** : 메모리 내용을 어떻게 표현하는지에 대한 정보. 예를 들어, 텍스트 문서나 벡터 데이터베이스.
- **메모리 연산** : 메모리 내용을 처리하는 방법. 예를 들어, 읽기, 쓰기, 삭제.

## 참고자료
| URL 이름 | URL |
| --- | --- |
| A Survey on the Memory Mechanism of Large Language Model based Agents | https://arxiv.org/html/2404.13501v1 |
| Implementing Memory in LLM Applications Using LangChain | https://www.codecademy.com/article/implementing-memory-in-llm-applications-using-lang-chain |
| How does ChatGPT remember? LLM Memory Explained. | https://mlexplained.blog/2024/03/03/how-does-chatgpt-remember-llm-memory-explained/ |
| How LLM Memory works : r/OpenAI - Reddit | https://www.reddit.com/r/OpenAI/comments/1aqksc3/how_llm_memory_works/ |
| MemLLM: Finetuning LLMs to Use An Explicit Read-Write Memory | https://arxiv.org/html/2404.11672v1 |