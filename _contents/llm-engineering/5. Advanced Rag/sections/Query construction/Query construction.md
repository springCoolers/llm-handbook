# Query Construction in LLM

## Summary
Query construction in LLM은 자연어 쿼리를 데이터베이스의 쿼리 언어로 변환하는 과정입니다. 이 과정은 구조화된 데이터(예: SQL 데이터베이스), 반구조화된 데이터(예: 문서 내의 테이블), 비구조화된 데이터(예: 벡터 데이터베이스 내의 텍스트)와 상호작용하는 데 중요합니다. LLM은 다양한 데이터 유형에 대한 쿼리 구성을 지원하며, 이는 데이터베이스의 언어를 이해하고 자연어 쿼리를 해당 언어로 변환하는 데 도움이 됩니다.

## Key Concepts
- **Query Construction** : 자연어 쿼리를 데이터베이스의 쿼리 언어로 변환하는 과정입니다.
- **Structured Data** : SQL 데이터베이스와 같은 구조화된 데이터는 사전 정의된 스키마를 가지고 있으며, 테이블이나 관계로 구성되어 정확한 쿼리 작업을 지원합니다.
- **Semi-structured Data** : 반구조화된 데이터는 구조화된 요소(예: 문서 내의 테이블)와 비구조화된 요소(예: 텍스트 또는 관계형 데이터베이스 내의 임베딩 열)를 혼합합니다.
- **Unstructured Data** : 비구조화된 데이터는 벡터 데이터베이스에 저장되며, 사전 정의된 모델이 없으며, 구조화된 메타데이터와 함께 저장되어 필터링을 지원합니다.

## References
| URL Name | URL |
| --- | --- |
| LangChain Blog | https://blog.langchain.dev/query-construction/ |
| Beehiiv | https://div.beehiiv.com/p/routing-query-construction |
| Timbr.ai | https://timbr.ai/blog/leveraging-sql-knowledge-graphs-for-accurate-llm-sql-query-generation/ |
| Haystack | https://haystack.deepset.ai/blog/business-intelligence-sql-queries-llm |
| YouTube | https://www.youtube.com/watch?v=Vd_8lS1iDBg |