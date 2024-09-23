# 프롬프트 가드레일(Prompt Guardrail)

## 요약
프롬프트 가드레일은 LLM(대형 언어 모델)에서 사용자 입력을 검증하고 제어하는 메커니즘입니다. 이는 모델이 부적절한 콘텐츠를 생성하거나 특정 지침을 위반하는 것을 방지하기 위해 사용됩니다. 프롬프트 가드레일은 입력 데이터를 검사하고, 모델의 출력을 검증하며, 필요에 따라 모델을 재실행하여 적절한 응답을 생성합니다.

## 주요 개념
- **입력 가드레일** : 사용자 입력을 검사하여 부적절한 콘텐츠를 필터링하고 모델이 올바른 데이터만 처리하도록 합니다.
- **출력 가드레일** : 모델의 출력을 검증하여 부적절한 콘텐츠가 생성되지 않도록 합니다.
- **가드레일 구현** : 가드레일을 구현하기 위해 다양한 프레임워크와 라이브러리를 사용할 수 있습니다. 예를 들어, Guardrails AI는 가드레일을 설정하고 관리하는 데 사용할 수 있는 오픈 소스 프레임워크입니다.

## 참고자료
| URL 이름 | URL |
| --- | --- |
| OpenAI Cookbook | https://cookbook.openai.com/examples/how_to_use_guardrails |
| Guardrails AI | https://www.guardrailsai.com/docs/the_guard |
| Towards Data Science | https://towardsdatascience.com/safeguarding-llms-with-guardrails-4f5d9f57cff2 |
| Neptune AI | https://neptune.ai/blog/llm-guardrails |