# Tree of Thoughts

## Summary
Tree of Thoughts (ToT)는 대형 언어 모델(Large Language Model, LLM)의 문제 해결 능력을 향상시키는 프레임워크입니다. 이 접근 방식은 인간의 사고 전략을 모방하여 LLM이 여러 가지 잠재적 솔루션을 체계적으로 탐색할 수 있도록 합니다. ToT는 사고를 트리 구조로 표현하여, 각 노드가 중간 단계의 사고를 나타내고, 이 사고를 평가하고 수정하는 과정을 통해 최종 솔루션에 도달합니다. 이 프레임워크는 LLM이 복잡한 문제를 해결할 때, 특히 수학적, 상징적, 상식적, 지식적 추론이 필요한 경우에 유용합니다.

## Key Concepts
- **Tree of Thoughts (ToT)** : LLM이 문제를 해결할 때, 여러 가지 잠재적 솔루션을 체계적으로 탐색하는 프레임워크입니다.
- **Thought Decomposer** : 큰 문제를 작은 단계로 나누는 모듈입니다.
- **Thought Generator** : 현재 사고에서 다음 단계의 후보를 생성하는 모듈입니다.
- **State Evaluator** : 후보 사고의 가치를 평가하는 모듈입니다.
- **Search Algorithm** : 트리 구조를 탐색하는 알고리즘으로, Breadth-First Search (BFS)와 Depth-First Search (DFS)가 포함됩니다.

## References
| URL Name | URL |
| --- | --- |
| Deepgram - Tree of Thoughts | https://deepgram.com/learn/tree-of-thoughts-prompting |
| IBM - Tree of Thoughts | https://www.ibm.com/topics/tree-of-thoughts |
| Prompting Guide - Tree of Thoughts | https://www.promptingguide.ai/techniques/tot |
| LinkedIn - Tree of Thoughts | https://www.linkedin.com/pulse/unlocking-llms-potential-tree-of-thought-prompting-albert-mao-abp2e |
| Reddit - Tree of Thoughts Prompt | https://www.reddit.com/r/LocalLLaMA/comments/1ak83am/tree_of_thoughts_tot_v1_prompt/ |