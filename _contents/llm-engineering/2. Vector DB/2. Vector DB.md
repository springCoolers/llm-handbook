# 2. Vector DB

```{tableofcontents}
```

The other big application buzzwords you’ve most likely encountered in some form are “tool use” and “agents”, or “agentic programming”. This typically starts with the ReAct framework we saw in the prompting section, then gets extended to elicit increasingly complex behaviors like software engineering (see the much-buzzed-about “Devin” system from Cognition, and several related open-source efforts like Devon/OpenDevin/SWE-Agent). There are many programming frameworks for building agent systems on top of LLMs, with Langchain and LlamaIndex being two of the most popular. There also seems to be some value in having LLMs rewrite their own prompts + evaluate their own partial outputs; this observation is at the heart of the DSPy framework (for “compiling” a program’s prompts, against a reference set of instructions or desired outputs) which has recently been seeing a lot of attention.
