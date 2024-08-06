# 4. Agents and Tools


The other big application buzzwords you’ve most likely encountered in some form are “tool use” and “agents”, or “agentic programming”. This typically starts with the ReAct framework we saw in the prompting section, then gets extended to elicit increasingly complex behaviors like software engineering (see the much-buzzed-about “Devin” system from Cognition, and several related open-source efforts like Devon/OpenDevin/SWE-Agent). There are many programming frameworks for building agent systems on top of LLMs, with Langchain and LlamaIndex being two of the most popular. There also seems to be some value in having LLMs rewrite their own prompts + evaluate their own partial outputs; this observation is at the heart of the DSPy framework (for “compiling” a program’s prompts, against a reference set of instructions or desired outputs) which has recently been seeing a lot of attention.

Resources:

- [“LLM Powered Autonomous Agents” (post)](https://lilianweng.github.io/posts/2023-06-23-agent/) from Lilian Weng
- [“A Guide to LLM Abstractions” (post)](https://www.twosigma.com/articles/a-guide-to-large-language-model-abstractions/) from Two Sigma
- [“DSPy Explained! (video)”](https://www.youtube.com/watch?v=41EfOY0Ldkc) by Connor Shorten

Also relevant are more narrowly-tailored (but perhaps more practical) applications related to databases — see these two [blog](https://neo4j.com/developer-blog/knowledge-graphs-llms-multi-hop-question-answering/) [posts](https://neo4j.com/blog/unifying-llm-knowledge-graph/) from Neo4J for discussion on applying LLMs to analyzing or constructing knowledge graphs, or this [blog post](https://numbersstation.ai/data-wrangling-with-fms-2/) from Numbers Station about applying LLMs to data wrangling tasks like entity matching.