# Splitting in LLM

## Summary
Splitting in LLM은 텍스트를 작은 단위로 나누는 프로세스를 말합니다. 이 프로세스는 LLM이 더 효과적으로 정보를 처리하고 이해할 수 있도록 도와줍니다. 텍스트를 나누는 방법에는 여러 가지가 있으며, 문장 단위로 나누는 sentence splitting, 토큰 수에 따라 나누는 max token splitting, 그리고 의미에 따라 나누는 semantic chunking 등이 있습니다. 각 방법은 장단점이 있으며, 적절한 chunking 전략을 선택하는 것이 중요합니다.

## Key Concepts
- **Sentence Splitting** : 텍스트를 문장 단위로 나누는 방법으로, 각 문장이 하나의 chunk가 됩니다.
- **Max Token Splitting** : 텍스트를 토큰 수에 따라 나누는 방법으로, 각 chunk는 최대 토큰 수를 가집니다.
- **Semantic Chunking** : 텍스트를 의미에 따라 나누는 방법으로, 각 chunk는 의미적으로 관련된 정보를 포함합니다.
- **Token-based Splitting** : 토큰 단위로 나누는 방법으로, LLM의 context window에 맞추어 chunk를 생성합니다.
- **Context-aware Splitting** : 문서의 구조와 계층을 고려하여 chunk를 생성하는 방법으로, header 정보를 보존합니다.

## References
| URL Name | URL |
| --- | --- |
| RAG Optimisation | https://www.luminis.eu/blog/rag-optimisation-use-an-llm-to-chunk-your-text-semantically/ |
| Mastering RAG | https://www.rungalileo.io/blog/mastering-rag-advanced-chunking-techniques-for-llm-applications |
| Document Splitting | https://dev.to/rutamstwt/split-conquer-mastering-document-splitting-in-langchain-1154 |
| Using an LLM to Split a Text Document | https://www.reddit.com/r/PromptEngineering/comments/19cruu1/using_an_llm_to_split_a_text_document/ |
| Chunking Strategies for LLM Applications | https://www.pinecone.io/learn/chunking-strategies/ |