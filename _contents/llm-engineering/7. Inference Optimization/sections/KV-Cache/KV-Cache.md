# KV-Cache

## Summary
KV-Cache는 Large Language Model (LLM)에서 사용되는 최적화 기법으로, 모델이 이전에 계산한 데이터를 저장하고 재사용하여 추론 시간을 단축합니다. KV-Cache는 모델이 이전에 계산한 키-값 벡터를 저장하여 추후의 계산에서 재사용할 수 있도록 합니다. 이는 모델이 긴 시퀀스를 처리할 때 특히 유용합니다. 그러나 KV-Cache는 GPU 메모리를大量으로 소비하여 모델의 성능과 컨텍스트 크기를 제한할 수 있습니다.

## Key Concepts
- **KV-Cache의 목적** : KV-Cache는 모델이 이전에 계산한 키-값 벡터를 저장하여 추후의 계산에서 재사용할 수 있도록 하여 추론 시간을 단축합니다.
- **KV-Cache의 구조** : KV-Cache는 각 토큰에 대해 계산된 키-값 벡터를 저장하며, 각 레이어와 각 헤드에 대해 별도의 캐시가 필요합니다.
- **KV-Cache의 크기** : KV-Cache의 크기는 모델의 크기와 시퀀스의 길이에 따라 달라지며, GPU 메모리를大量으로 소비할 수 있습니다.
- **KV-Cache의 최적화** : KV-Cache의 최적화를 위해 다양한 기법이 사용되며, 이는 모델의 성능과 메모리 사용량을 개선할 수 있습니다.

## References
| URL 이름 | URL |
| --- | --- |
| Techniques for KV Cache Optimization | https://www.omrimallis.com/posts/techniques-for-kv-cache-optimization/ |
| SqueezeAttention: 2D Management of KV-Cache in LLM Inference | https://arxiv.org/html/2404.04793v1 |
| LLM Jargons Explained: Part 4 - KV Cache | https://www.youtube.com/watch?v=z07GStMex4w |
| How KV cache is valid in LLM transformer | https://www.reddit.com/r/MachineLearning/comments/1b0ob2m/d_how_kv_cache_is_valid_in_llm_transformer/ |
| LLM profiling guides KV cache optimization | https://www.microsoft.com/en-us/research/blog/llm-profiling-guides-kv-cache-optimization/ |