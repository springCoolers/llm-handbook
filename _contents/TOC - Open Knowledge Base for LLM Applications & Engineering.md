

## API + Prompt Engineering  

### proprietary APIs
- **LLM APIs**: APIs are a convenient way to deploy LLMs. This space is divided between private LLMs ([OpenAI](https://platform.openai.com/), [Google](https://cloud.google.com/vertex-ai/docs/generative-ai/learn/overview), [Anthropic](https://docs.anthropic.com/claude/reference/getting-started-with-the-api), [Cohere](https://docs.cohere.com/docs), etc.) and open-source LLMs ([OpenRouter](https://openrouter.ai/), [Hugging Face](https://huggingface.co/inference-api), [Together AI](https://www.together.ai/), etc.) 

### prompt engineering (playground)
- Few-Shot Examples
- Chain-of-Thought
- Retrieval-Augmented Generation (RAG)
- ReAct


📚 **References**:
- Awesome-prompt-engineering - Open Source Repo 
- This [blog post](https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/) by Lilian Weng discusses several of the most dominant approaches, [guide](https://www.promptingguide.ai/techniques) has decent coverage and examples for a wider range of the prominent techniques used today. 
- Keyword-searching on Twitter/X or LinkedIn will give you plenty more. We’ll also dig deeper into RAG and agent methods in later chapters.
### Sampling and Structured Outputs

While typical LLM inference samples tokens one at a time, there are number of parameters controlling the token distribution (temperature, top_p, top_k) which can be modified to control the variety of responses, as well as non-greedy decoding strategies that allow some degree of “lookahead”. This [blog post](https://towardsdatascience.com/decoding-strategies-in-large-language-models-9733a8f70539) by Maxime Labonne does a nice job discussing several of them.

Sometimes we also want our outputs to follow a particular structure, particularly if we are using LLMs as a component of a larger system rather than as just a chat interface. Few-shot prompting works okay, but not all the time, particularly as output schemas become more complicated. For schema types like JSON, Pydantic and Outlines are popular tools for constraining the output structure from LLMs. Some useful resources:

- [Pydantic Concepts](https://docs.pydantic.dev/latest/concepts/models/)
- [Outlines for JSON](https://outlines-dev.github.io/outlines/reference/json/)
- [Outlines review](https://michaelwornow.net/2023/12/29/outlines-demo) by Michael Wornow

- **Structuring outputs**: Many tasks require a structured output, like a strict template or a JSON format. Libraries like [LMQL](https://lmql.ai/), [Outlines](https://github.com/outlines-dev/outlines), [Guidance](https://github.com/guidance-ai/guidance), etc. can be used to guide the generation and respect a given structure.
	- [Outlines - Quickstart](https://outlines-dev.github.io/outlines/quickstart/): List of guided generation techniques enabled by Outlines.
	- [LMQL - Overview](https://lmql.ai/docs/language/overview.html): Introduction to the LMQL language.

### Evaluation : 

- Building Test sets: **If you expect the models you use to change at all, it’s important to unit-test all your prompts using evaluation examples.**


### Prompt tuning

A cool idea that is between prompting and finetuning is **[prompt tuning](https://arxiv.org/abs/2104.08691)**, introduced by Leister et al. in 2021. Starting with a prompt, instead of changing this prompt, you programmatically change the embedding of this prompt. For prompt tuning to work, you need to be able to input prompts’ embeddings into your LLM model and generate tokens from these embeddings, which currently, can only be done with open-source LLMs and not in OpenAI API. On T5, prompt tuning appears to perform much better than prompt engineering and can catch up with model tuning (see image below).





## Vector Storage & RAG

### Ingesting Splitting  
### Embedding
### Reranking
- stuck in the middle - 

- Orchestrators
### Retreivers
	- multi-query retriever, 
	- [HyDE](https://arxiv.org/abs/2212.10496)
- Memory To remember previous instructions and answers, LLMs and chatbots like ChatGPT add this history to their context window. This buffer can be improved with summarization (e.g., using a smaller LLM), a vector store + RAG, etc.

### Evaluation
We need to evaluate both the document retrieval (context precision and recall) and generation stages (faithfulness and answer relevancy). It can be simplified with tools [Ragas](https://github.com/explodinggradients/ragas/tree/main) and [DeepEval](https://github.com/confident-ai/deepeval).

### Query construction
Structured data stored in traditional databases requires a specific query language like SQL, Cypher, metadata, etc. We can directly translate the user instruction into a query to access the data with query construction.


- **Post-processing**: Final step that processes the inputs that are fed to the LLM. It enhances the relevance and diversity of documents retrieved with re-ranking, [RAG-fusion](https://github.com/Raudaschl/rag-fusion), and classification.
- **Program LLMs**: Frameworks like [DSPy](https://github.com/stanfordnlp/dspy) allow you to optimize prompts and weights based on automated evaluations in a programmatic way.


📚 **References**:

- [Llamaindex - High-level concepts](https://docs.llamaindex.ai/en/stable/getting_started/concepts.html): Main concepts to know when building RAG pipelines.
- [Pinecone - Retrieval Augmentation](https://www.pinecone.io/learn/series/langchain/langchain-retrieval-augmentation/): Overview of the retrieval augmentation process.
- [LangChain - Q&A with RAG](https://python.langchain.com/docs/use_cases/question_answering/quickstart): Step-by-step tutorial to build a typical RAG pipeline.
- [LangChain - Memory types](https://python.langchain.com/docs/modules/memory/types/): List of different types of memories with relevant usage.
- [RAG pipeline - Metrics](https://docs.ragas.io/en/stable/concepts/metrics/index.html): Overview of the main metrics used to evaluate RAG pipelines.

- [“Deconstructing RAG”](https://blog.langchain.dev/deconstructing-rag/) from Langchain
- [“Building RAG with Open-Source and Custom AI Models”](https://www.bentoml.com/blog/building-rag-with-open-source-and-custom-ai-models) from Chaoyu Yang



## Agents and tools + Advanced RAG: 
Agents augment LLMs by automatically selecting the most relevant tools to provide an answer. These tools can be as simple as using Google or Wikipedia, or more complex like a Python interpreter or Jira.

The other big application buzzwords you’ve most likely encountered in some form are “tool use” and “agents”, or “agentic programming”. This typically starts with the ReAct framework we saw in the prompting section, then gets extended to elicit increasingly complex behaviors like software engineering (see the much-buzzed-about “Devin” system from Cognition, and several related open-source efforts like Devon/OpenDevin/SWE-Agent). There are many programming frameworks for building agent systems on top of LLMs, with Langchain and LlamaIndex being two of the most popular. There also seems to be some value in having LLMs rewrite their own prompts + evaluate their own partial outputs; this observation is at the heart of the DSPy framework (for “compiling” a program’s prompts, against a reference set of instructions or desired outputs) which has recently been seeing a lot of attention.

Resources:

- [“LLM Powered Autonomous Agents” (post)](https://lilianweng.github.io/posts/2023-06-23-agent/) from Lilian Weng
- [“A Guide to LLM Abstractions” (post)](https://www.twosigma.com/articles/a-guide-to-large-language-model-abstractions/) from Two Sigma
- [“DSPy Explained! (video)”](https://www.youtube.com/watch?v=41EfOY0Ldkc) by Connor Shorten

Also relevant are more narrowly-tailored (but perhaps more practical) applications related to databases — see these two [blog](https://neo4j.com/developer-blog/knowledge-graphs-llms-multi-hop-question-answering/) [posts](https://neo4j.com/blog/unifying-llm-knowledge-graph/) from Neo4J for discussion on applying LLMs to analyzing or constructing knowledge graphs, or this [blog post](https://numbersstation.ai/data-wrangling-with-fms-2/) from Numbers Station about applying LLMs to data wrangling tasks like entity matching.


### Post-processing: 
Final step that processes the inputs that are fed to the LLM. It enhances the relevance and diversity of documents retrieved with re-ranking, [RAG-fusion](https://github.com/Raudaschl/rag-fusion), and classification.

### Program LLMs
Frameworks like [DSPy](https://github.com/stanfordnlp/dspy) allow you to optimize prompts and weights based on automated evaluations in a programmatic way.

### Query construction
Structured data stored in traditional databases requires a specific query language like SQL, Cypher, metadata, etc. We can directly translate the user instruction into a query to access the data with query construction.


## Finetuning Open Source Models

### List of OS Models
The [Hugging Face Hub](https://huggingface.co/models) is a great place to find LLMs. You can directly run some of them in [Hugging Face Spaces](https://huggingface.co/spaces), or download and run them locally in apps like [LM Studio](https://lmstudio.ai/) or through the CLI with [llama.cpp](https://github.com/ggerganov/llama.cpp) or [Ollama](https://ollama.ai/).

### Local deployment: 
Privacy is an important advantage that open-source LLMs have over private ones. Local LLM servers ([LM Studio](https://lmstudio.ai/), [Ollama](https://ollama.ai/), [oobabooga](https://github.com/oobabooga/text-generation-webui), [kobold.cpp](https://github.com/LostRuins/koboldcpp), etc.) capitalize on this advantage to power local apps. 
### Benchmarking

Beyond the standard numerical performance measures used during LLM training like cross-entropy loss and [perplexity](https://medium.com/@priyankads/perplexity-of-language-models-41160427ed72), the true performance of frontier LLMs is more commonly judged according to a range of benchmarks, or “evals”. Common types of these are:

- Human-evaluated outputs (e.g. [LMSYS Chatbot Arena](https://chat.lmsys.org/))
- AI-evaluated outputs (as used in [RLAIF](https://argilla.io/blog/mantisnlp-rlhf-part-4/))
- Challenge question sets (e.g. those in HuggingFace’s [LLM Leaderboard](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard))

See the [slides](https://web.stanford.edu/class/cs224n/slides/cs224n-spr2024-lecture11-evaluation-yann.pdf) from Stanford’s CS224n for an overview. This [blog post](https://www.jasonwei.net/blog/evals) by Jason Wei and [this one](https://humanloop.com/blog/evaluating-llm-apps?utm_source=newsletter&utm_medium=sequence&utm_campaign=) by Peter Hayes do a nice job discussing the challenges and tradeoffs associated with designing good evaluations, and highlighting a number of the most prominent ones used today. The documentation for the open source framework [inspect-ai](https://ukgovernmentbeis.github.io/inspect_ai/) also features some useful discussion around designing benchmarks and reliable evaluation pipelines.

### Instruct Fine-Tuning

Instruct fine-tuning (or “instruction tuning”, or “supervised finetuning”, or “chat tuning” – the boundaries here are a bit fuzzy) is the primary technique used (at least initially) for coaxing LLMs to conform to a particular style or format. Here, data is presented as a sequence of (input, output) pairs where the input is a user question to answer, and the model’s goal is to predict the output – typically this also involves adding special “start”/”stop”/”role” tokens and other masking techniques, enabling the model to “understand” the difference between the user’s input and its own outputs. This technique is also widely used for task-specific finetuning on datasets with a particular kind of problem structure (e.g. translation, math, general question-answering).

See this [blog post](https://newsletter.ruder.io/p/instruction-tuning-vol-1) from Sebastian Ruder or this [video](https://www.youtube.com/watch?v=YoVek79LFe0) from Shayne Longpre for short overviews.

### Low-Rank Adapters (LoRA)

While pre-training (and “full finetuning”) requires applying gradient updates to all parameters of a model, this is typically impractical on consumer GPUs or home setups; fortunately, it’s often possible to significantly reduce the compute requirements by using parameter-efficient finetuning (PEFT) techniques like Low-Rank Adapters (LoRA). This can enable competitive performance even with relatively small datasets, particularly for application-specific use cases. The main idea behind LoRA is to train each weight matrix in a low-rank space by “freezing” the base matrix and training a factored representation with much smaller inner dimension, which is then added to the base matrix.

📚 **Resources**:

- LoRA paper walkthrough [(video, part 1)](https://youtu.be/dA-NhCtrrVE?si=TpJkPfYxngQQ0iGj)
- LoRA code demo [(video, part 2)](https://youtu.be/iYr1xZn26R8?si=aG0F8ws9XslpZ4ur)
- [“Parameter-Efficient LLM Finetuning With Low-Rank Adaptation”](https://sebastianraschka.com/blog/2023/llm-finetuning-lora.html) by Sebastian Raschka
- [“Practical Tips for Finetuning LLMs Using LoRA”](https://magazine.sebastianraschka.com/p/practical-tips-for-finetuning-llms) by Sebastian Raschka

Additionally, an “decomposed” LoRA variant called DoRA has been gaining popularity in recent months, often yielding performance improvements; see this [post](https://magazine.sebastianraschka.com/p/lora-and-dora-from-scratch) from Sebastian Raschka for more detail

### Reward Models and RLHF

One of the most prominent techniques for “aligning” a language model is Reinforcement Learning from Human Feedback (RLHF); here, we typically assume that an LLM has already been instruction-tuned to respect a chat style, and that we additionally have a “reward model” which has been trained on human preferences. Given pairs of differing outputs to an input, where a preferred output has been chosen by a human, the learning objective of the reward model is to predict the preferred output, which involves implicitly learning preference “scores”. This allows bootstrapping a general representation of human preferences (at least with respect to the dataset of output pairs), which can be used as a “reward simulator” for continual training of a LLM using RL policy gradient techniques like PPO.

For overviews, see the posts [“Illustrating Reinforcement Learning from Human Feedback (RLHF)”](https://huggingface.co/blog/rlhf) from Hugging Face and [“Reinforcement Learning from Human Feedback”](https://huyenchip.com/2023/05/02/rlhf.html) from Chip Huyen, and/or this [RLHF talk](https://www.youtube.com/watch?v=2MBJOuVq380) by Nathan Lambert. Further, this [post](https://sebastianraschka.com/blog/2024/research-papers-in-march-2024.html) from Sebastian Raschka dives into RewardBench, and how reward models themselves can be evaluated against each other by leveraging ideas from Direct Preference Optimization, another prominent approach for aligning LLMs with human preference data.

### Direct Preference Optimization Methods

The space of alignment algorithms seems to be following a similar trajectory as we saw with stochastic optimization algorithms a decade ago. In this an analogy, RLHF is like SGD — it works, it’s the original, and it’s also become kind of a generic “catch-all” term for the class of algorithms that have followed it. Perhaps DPO is AdaGrad, and in the year since its release there’s been a rapid wave of further algorithmic developments along the same lines (KTO, IPO, ORPO, etc.), whose relative merits are still under active debate. Maybe a year from now, everyone will have settled on a standard approach which will become the “Adam” of alignment.

For an overview of the theory behind DPO see this [blog post](https://towardsdatascience.com/understanding-the-implications-of-direct-preference-optimization-a4bbd2d85841) Matthew Gunton; this [blog post](https://huggingface.co/blog/dpo-trl) from Hugging Face features some code and demonstrates how to make use of DPO in practice. Another [blog post](https://huggingface.co/blog/pref-tuning) from Hugging Face also discuss


### Context Scaling


Beyond task specification or alignment, another common goal of finetuning is to increase the effective context length of a model, either via additional training, adjusting parameters for positional encodings, or both. Even if adding more tokens to a model’s context can “type-check”, training on additional longer examples is generally necessary if the model may not have seen such long sequences during pretraining.


### Distillation and Merging

Here we’ll look at two very different methods of consolidating knowledge across LLMs — distillation and merging. Distillation was first popularized for BERT models, where the goal is to “distill” the knowledge and performance of a larger model into a smaller one (at least for some tasks) by having it serve as a “teacher” during the smaller model’s training, bypassing the need for large quantities of human-labeled data.

Some resources on distillation:

- [“Smaller, faster, cheaper, lighter: Introducing DistilBERT, a distilled version of BERT”](https://medium.com/huggingface/distilbert-8cf3380435b5) from Hugging Face
- [“LLM distillation demystified: a complete guide”](https://snorkel.ai/llm-distillation-demystified-a-complete-guide/) from Snorkel AI
- [“Distilling Step by Step” blog](https://blog.research.google/2023/09/distilling-step-by-step-outperforming.html) from Google Research

Merging, on the other hand, is much more of a “wild west” technique, largely used by open-source engineers who want to combine the strengths of multiple finetuning efforts. It’s kind of wild to me that it works at all, and perhaps grants some credence to “linear representation hypotheses” (which will appear in the next section when we discuss interpretability). The idea is basically to take two different finetunes of the same base model and just average their weights. No training required. Technically, it’s usually “spherical interpolation” (or “slerp”), but this is pretty much just fancy averaging with a normalization step. For more details, see the post [Merge Large Language Models with mergekit](https://huggingface.co/blog/mlabonne/merge-models) by Maxime Labonne.



## UI + Deploy (=Web / Platform)

- **Demo building** : Streamlit / Gradio
- **Server deployment**: Deploy LLMs at scale requires cloud (see also [SkyPilot](https://skypilot.readthedocs.io/en/latest/)) or on-prem infrastructure and often leverage optimized text generation frameworks like [TGI](https://github.com/huggingface/text-generation-inference), [vLLM](https://github.com/vllm-project/vllm/tree/main), etc.
- **Edge deployment**: In constrained environments, high-performance frameworks like [MLC LLM](https://github.com/mlc-ai/mlc-llm) and [mnn-llm](https://github.com/wangzhaode/mnn-llm/blob/master/README_en.md) can deploy LLM in web browsers, Android, and iOS.

📚 **References**:

- [Streamlit - Build a basic LLM app](https://docs.streamlit.io/knowledge-base/tutorials/build-conversational-apps): Tutorial to make a basic ChatGPT-like app using Streamlit.
- [HF LLM Inference Container](https://huggingface.co/blog/sagemaker-huggingface-llm): Deploy LLMs on Amazon SageMaker using Hugging Face's inference container.
- [Philschmid blog](https://www.philschmid.de/) by Philipp Schmid: Collection of high-quality articles about LLM deployment using Amazon SageMaker.
- [Optimizing latence](https://hamel.dev/notes/llm/inference/03_inference.html) by Hamel Husain: Comparison of TGI, vLLM, CTranslate2, and mlc in terms of throughput and latency.
## Inference Optimization 

- **Key-value cache**: Understand the key-value cache and the improvements introduced in [Multi-Query Attention](https://arxiv.org/abs/1911.02150) (MQA) and [Grouped-Query Attention](https://arxiv.org/abs/2305.13245) (GQA).
- **Speculative decoding**: Use a small model to produce drafts that are then reviewed by a larger model to speed up text generation.

### Chapter 35: Parameter Quantization

With the rapid increase in parameter counts for leading LLMs and difficulties (both in cost and availability) in acquiring GPUs to run models on, there’s been a growing interest in quantizing LLM weights to use fewer bits each, which can often yield comparable output quality with a 50-75% (or more) reduction in required memory. Typically this shouldn’t be done naively; Tim Dettmers, one of the pioneers of several modern quantization methods (LLM.int8(), QLoRA, bitsandbytes) has a great [blog post](https://timdettmers.com/2022/08/17/llm-int8-and-emergent-features/) for understanding quantization principles, and the need for mixed-precision quantization as it relates to emergent features in large-model training. Other popular methods and formats are GGUF (for llama.cpp), AWQ, HQQ, and GPTQ; see this [post](https://www.tensorops.ai/post/what-are-quantized-llms) from TensorOps for an overview, and this [post](https://www.maartengrootendorst.com/blog/quantization/) from Maarten Grootendorst for a discussion of their tradeoffs.

In addition to enabling inference on smaller machines, quantization is also popular for parameter-efficient training; in QLoRA, most weights are quantized to 4-bit precision and frozen, while active LoRA adapters are trained in 16-bit precision. See this [talk](https://www.youtube.com/watch?v=fQirE9N5q_Y) from Tim Dettmers, or this [blog](https://huggingface.co/blog/4bit-transformers-bitsandbytes) from Hugging Face for overviews. This [blog post](https://www.answer.ai/posts/2024-03-14-fsdp-qlora-deep-dive.html) from Answer.AI also shows how to combine QLoRA with FSDP for efficient finetuning of 70B+ parameter models on consumer GPUs.

### Chapter 36: Speculative Decoding

The basic idea behind speculative decoding is to speed up inference from a larger model by primarily sampling tokens from a much smaller model and occasionally applying corrections (e.g. every _N_ tokens) from the larger model whenever the output distributions diverge. These batched consistency checks tend to be much faster than sampling _N_ tokens directly, and so there can be large overall speedups if the token sequences from smaller model only diverge periodically.

See this [blog post](https://jaykmody.com/blog/speculative-sampling/) from Jay Mody for a walkthrough of the original paper, and this PyTorch [article](https://pytorch.org/blog/hitchhikers-guide-speculative-decoding/) for some evaluation results. There’s a nice [video](https://www.youtube.com/watch?v=hm7VEgxhOvk) overview from Trelis Research as well.

### Chapter 37: FlashAttention

Computing attention matrices tends to be a primary bottleneck in inference and training for Transformers, and FlashAttention has become one of the most widely-used techniques for speeding it up. In contrast to some of the techniques we’ll see in [Section 7](https://genai-handbook.github.io/#s7) which _approximate_ attention with a more concise representation (occurring some representation error as a result), FlashAttention is an _exact_ representation whose speedup comes from hardware-aware impleemntation. It applies a few tricks — namely, tiling and recomputation — to decompose the expression of attention matrices, enabling significantly reduced memory I/O and faster wall-clock performance (even with slightly increasing the required FLOPS).

Resources:

- [Talk](https://www.youtube.com/watch?v=gMOAud7hZg4) by Tri Dao (author of FlashAttention)
- [ELI5: FlashAttention](https://gordicaleksa.medium.com/eli5-flash-attention-5c44017022ad) by Aleksa Gordić

### Chapter 38: Key-Value Caching and Paged Attention

As noted in the [NVIDIA blog](https://developer.nvidia.com/blog/mastering-llm-techniques-inference-optimization/) referenced above, key-value caching is fairly standard in Transformer implementation matrices to avoid redundant recomputation of attention. This enables a tradeoff between speed and resource utilization, as these matrices are kept in GPU VRAM. While managing this is fairly straightforward for a single “thread” of inference, a number of complexities arise when considering parallel inference or multiple users for a single hosted model instance. How can you avoid recomputing values for system prompts and few-shot examples? When should you evict cache elements for a user who may or may not want to continue a chat session? PagedAttention and its popular implementation [vLLM](https://docs.vllm.ai/en/stable/) addresses this by leveraging ideas from classical paging in operating systems, and has become a standard for self-hosted multi-user inference servers.

Resources:

- [The KV Cache: Memory Usage in Transformers](https://www.youtube.com/watch?v=80bIUggRJf4) (video, Efficient NLP)
- [Fast LLM Serving with vLLM and PagedAttention](https://www.youtube.com/watch?v=5ZlavKF_98U) (video, Anyscale)
- vLLM [blog post](https://blog.vllm.ai/2023/06/20/vllm.html)

### Chapter 39: CPU Offloading

The primary method used for running LLMs either partially or entirely on CPU (vs. GPU) is llama.cpp. See [here](https://www.datacamp.com/tutorial/llama-cpp-tutorial) for a high-level overview; llama.cpp serves as the backend for a number of popular self-hosted LLM tools/frameworks like LMStudio and Ollama. Here’s a [blog post](https://justine.lol/matmul/) with some technical details about CPU performance improvements.


📚 **References**:

- [GPU Inference](https://huggingface.co/docs/transformers/main/en/perf_infer_gpu_one) by Hugging Face: Explain how to optimize inference on GPUs.
- [LLM Inference](https://www.databricks.com/blog/llm-inference-performance-engineering-best-practices) by Databricks: Best practices for how to optimize LLM inference in production.
- [Optimizing LLMs for Speed and Memory](https://huggingface.co/docs/transformers/main/en/llm_tutorial_optimization) by Hugging Face: Explain three main techniques to optimize speed and memory, namely quantization, Flash Attention, and architectural innovations.
- [Assisted Generation](https://huggingface.co/blog/assisted-generation) by Hugging Face: HF's version of speculative decoding, it's an interesting blog post about how it works with code to implement it.



## Hacking & Guardrails

- **Prompt hacking**: Different techniques related to prompt engineering, including prompt injection (additional instruction to hijack the model's answer), data/prompt leaking (retrieve its original data/prompt), and jailbreaking (craft prompts to bypass safety features).
- **Backdoors**: Attack vectors can target the training data itself, by poisoning the training data (e.g., with false information) or creating backdoors (secret triggers to change the model's behavior during inference).
- **Defensive measures**: The best way to protect your LLM applications is to test them against these vulnerabilities (e.g., using red teaming and checks like [garak](https://github.com/leondz/garak/)) and observe them in production (with a framework like [langfuse](https://github.com/langfuse/langfuse)).

📚 **References**:

- [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) by HEGO Wiki: List of the 10 most critic vulnerabilities seen in LLM applications.
- [Prompt Injection Primer](https://github.com/jthack/PIPE) by Joseph Thacker: Short guide dedicated to prompt injection for engineers.
- [LLM Security](https://llmsecurity.net/) by [@llm_sec](https://twitter.com/llm_sec): Extensive list of resources related to LLM security.
- [Red teaming LLMs](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/red-teaming) by Microsoft: Guide on how to perform red teaming with LLMs.









# AI Strategy & uses

- Building LLM applications for production https://huyenchip.com/2023/04/11/llm-engineering.html



# 이건 뭐야... 무서워 
## Chapter 31: LLMs for Synthetic Data

An increasing number of applications are making use of LLM-generated data for training or evaluations, including distillation, dataset augmentation, AI-assisted evaluation and labeling, self-critique, and more. This [post](https://www.promptingguide.ai/applications/synthetic_rag) demonstrates how to construct such a synthetic dataset (in a RAG context), and this [post](https://argilla.io/blog/mantisnlp-rlhf-part-4/) from Argilla gives an overview of RLAIF, which is often a popular alternative to RLHF, given the challenges associated with gathering pairwise human preference data. AI-assisted feedback is also a central component of the “Constitutional AI” alignment method pioneered by Anthropic (see their [blog](https://www.anthropic.com/news/claudes-constitution) for an overview).

## Chapter 32: Representation Engineering

Representation Engineering is a new and promising technique for fine-grained steering of language model outputs via “control vectors”. Somewhat similar to LoRA adapters, it has the effect of adding low-rank biases to the weights of a network which can elicit particular response styles (e.g. “humorous”, “verbose”, “creative”, “honest”), yet is much more computationally efficient and can be implemented without any training required. Instead, the method simply looks at differences in activations for pairs of inputs which vary along the axis of interest (e.g. honesty), which can be generated synthetically, and then performs dimensionality reduction.

See this short [blog post](https://www.safe.ai/blog/representation-engineering-a-new-way-of-understanding-models) from Center for AI Safety (who pioneered the method) for a brief overview, and this [post](https://vgel.me/posts/representation-engineering/) from Theia Vogel for a technical deep-dive with code examples. Theia also walks through the method in this [podcast episode](https://www.youtube.com/watch?v=PkA4DskA-6M).

## Chapter 33: Mechanistic Interpretability

Mechanistic Interpretability (MI) is the dominant paradigm for understanding the inner workings of LLMs by identifying sparse representations of “features” or “circuits” encoded in model weights. Beyond enabling potential modification or explanation of LLM outputs, MI is often viewed as an important step towards potentially “aligning” increasingly powerful systems. Most of the references here will come from [Neel Nanda](https://www.neelnanda.io/), a leading researcher in the field who’s created a large number of useful educational resources about MI across a range of formats:

- [“A Comprehensive Mechanistic Interpretability Explainer & Glossary”](https://www.neelnanda.io/mechanistic-interpretability/glossary)
- [“An Extremely Opinionated Annotated List of My Favourite Mechanistic Interpretability Papers”](https://www.neelnanda.io/mechanistic-interpretability/favourite-papers)
- [“Mechanistic Interpretability Quickstart Guide”](https://www.lesswrong.com/posts/jLAvJt8wuSFySN975/mechanistic-interpretability-quickstart-guide) (Neel Nanda on LessWrong)
- [“How useful is mechanistic interpretability?”](https://www.lesswrong.com/posts/tEPHGZAb63dfq2v8n/how-useful-is-mechanistic-interpretability) (Neel and others, discussion on LessWrong)
- [“200 Concrete Problems In Interpretability”](https://docs.google.com/spreadsheets/d/1oOdrQ80jDK-aGn-EVdDt3dg65GhmzrvBWzJ6MUZB8n4/edit#gid=0) (Annotated spreadsheet of open problems from Neel)

Additionally, the articles [“Toy Models of Superposition”](https://transformer-circuits.pub/2022/toy_model/index.html) and [“Scaling Monosemanticity: Extracting Interpretable Features from Claude 3 Sonnet”](https://transformer-circuits.pub/2024/scaling-monosemanticity/index.html) from Anthropic are on the longer side, but feature a number of great visualizations and demonstrations of these concepts.

## Chapter 34: Linear Representation Hypotheses

An emerging theme from several lines of interpretability research has been the observation that internal representations of features in Transformers are often “linear” in high-dimensional space (a la Word2Vec). On one hand this may appear initially surprising, but it’s also essentially an implicit assumption for techniques like similarity-based retrieval, merging, and the key-value similarity scores used by attention. See this [blog post](https://www.beren.io/2023-04-04-DL-models-are-secretly-linear/) by Beren Millidge, this [talk](https://www.youtube.com/watch?v=ko1xVcyDt8w) from Kiho Park, and perhaps at least skim the paper [“Language Models Represent Space and Time”](https://arxiv.org/pdf/2310.02207) for its figures.

