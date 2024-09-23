# 서버
## 요약
LLM(대형 언어 모델)에서 서버는 사용자 요청을 처리하고 모델에 전달하는 역할을 합니다. 서버는 HTTP/gRPC 요청을 관리하고, 요청을 큐에 저장하여 모델이 처리할 수 있도록 합니다. 또한, 서버는 모델의 성능을 측정하는 지표인 처리량(throughput)과 지연 시간(latency)을 제공합니다. 서버는 다양한 프레임워크와 함께 사용될 수 있으며, 모델을 효율적으로 배포하고 관리하는 데 중요한 역할을 합니다.

## 주요 개념
- **서버 역할** : 사용자 요청을 처리하고 모델에 전달하는 역할을 합니다.
- **요청 큐** : 사용자 요청을 저장하여 모델이 처리할 수 있도록 합니다.
- **처리량(throughput)** : 모델이 처리할 수 있는 요청의 수를 나타냅니다.
- **지연 시간(latency)** : 모델이 요청을 처리하는 데 걸리는 시간을 나타냅니다.
- **배치 처리** : 여러 요청을 한 번에 처리하여 효율성을 높입니다.

## 참고 자료
| URL 이름 | URL |
| --- | --- |
| Run:ai | https://www.run.ai/blog/serving-large-language-models |
| AI on OpenShift | https://ai-on-openshift.io/generative-ai/llm-serving/ |
| LM Studio | https://lmstudio.ai/docs/local-server |
| mariochavez/llm_server | https://github.com/mariochavez/llm_server |
| Puget Systems | https://www.pugetsystems.com/labs/hpc/llm-server-setup-part-1-base-os/ |