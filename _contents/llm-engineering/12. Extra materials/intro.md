# 12. Extra materials - from GenAI 핸드북

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
