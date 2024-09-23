# Finetuning Basics
## Summary
Finetuning in Large Language Models (LLMs) is a process that adapts pre-trained models to specific tasks or domains by updating their parameters on a new dataset. This process enhances the model's performance on targeted applications, making it crucial for domain-specific tasks where pre-trained models lack specialized knowledge. Finetuning involves various techniques, including unsupervised, supervised, and instruction-based methods, each with its own advantages and limitations. The process typically includes preparing a high-quality dataset that is representative of the task and updating the model weights to better capture the underlying patterns and complexities in the data.

## Key Concepts
- **Finetuning**: A process that adapts pre-trained LLMs to specific tasks or domains by updating their parameters on a new dataset.
- **Unsupervised Finetuning**: Involves exposing the LLM to a large corpus of unlabelled text from the target domain to refine its understanding of language.
- **Supervised Finetuning**: Requires labelled data tailored to the target task, such as text classification or sentiment analysis.
- **Instruction-Based Finetuning**: Uses natural language instructions to guide the LLM, useful for creating specialized assistants.
- **Data Requirements**: High-quality, representative, and sufficiently specified datasets are essential for effective finetuning.
- **Model Selection**: Choosing the most suitable pre-trained model for finetuning is crucial, considering factors such as model size, complexity, and original training data.

## References
| URL Name | URL |
| --- | --- |
| Finetuning in Large Language Models - Oracle Blogs | https://blogs.oracle.com/ai-and-datascience/post/finetuning-in-large-language-models |
| Getting started with LLM fine-tuning - Microsoft Learn | https://learn.microsoft.com/ja-jp/ai/playbook/technology-guidance/generative-ai/working-with-llms/fine-tuning |
| The Ultimate Guide to LLM Fine Tuning: Best Practices & Tools - Lakera AI | https://www.lakera.ai/blog/llm-fine-tuning-guide |
| The Ultimate Guide to Fine-Tuning LLMs from Basics to Breakthroughs - arXiv | https://arxiv.org/html/2408.13296v1 |
| My experience on starting with fine tuning LLMs with custom data - Reddit | https://www.reddit.com/r/LocalLLaMA/comments/14vnfh2/my_experience_on_starting_with_fine_tuning_llms/ |