# Retrievers in LLM

## Summary
Retrievers in Large Language Models (LLMs)는 LLM의 성능을 향상시키기 위해 외부 정보를 검색하고 제공하는 역할을 합니다. Retrieval-augmented Generation (RAG)과 같은 기술은 LLM이 외부 정보를 검색하고 이를 입력 컨텍스트에 통합하여 최종 예측을 수행할 수 있도록 합니다. 이 과정에서 retriever와 LLM의 선호도 차이를 해결하는 것이 중요하며, 이를 위해 retriever와 LLM을 함께 fine-tuning하거나 LLM만 fine-tuning하는 방법이 있습니다.

## Key Concepts
- **Retrieval-augmented Generation (RAG)** : LLM이 외부 정보를 검색하고 이를 입력 컨텍스트에 통합하여 최종 예측을 수행하는 기술입니다.
- **Retriever** : 외부 정보를 검색하고 LLM에 제공하는 모듈입니다.
- **Fine-tuning** : retriever와 LLM을 함께 또는 개별적으로 학습하여 선호도 차이를 해결하는 방법입니다.
- **Preference Gap** : retriever와 LLM의 선호도 차이를 의미하며, 이를 해결하는 것이 중요합니다.

## References
| URL Name | URL |
| --- | --- |
| Bridging the Preference Gap between Retrievers and LLMs | https://arxiv.org/html/2401.06954v1 |
| Langchain: How to view the context my retriever used when invoke | https://stackoverflow.com/questions/78322637/langchain-how-to-view-the-context-my-retriever-used-when-invoke |
| Hi can we have multiple retrievers in the retrievalQA chain? | https://github.com/langchain-ai/langchain/discussions/16898 |
| Neural Retrievers are Biased Towards LLM-Generated Content | https://arxiv.org/abs/2310.20501 |
| How to include metadata of retrieved content in the Output of retriever | https://www.reddit.com/r/LangChain/comments/1b1k4p7/how_to_include_metadata_of_retrieved_content_in/ |