# LoRA

## Summary
LoRA (Low-Rank Adaptation) is a technique used for fine-tuning large language models (LLMs) in a parameter-efficient way. It modifies the fine-tuning process by freezing the original model weights and applying changes to a separate set of weights, which are then added to the original parameters. This approach significantly reduces the memory and computational requirements for fine-tuning, making it possible for smaller organizations and individual developers to train specialized LLMs over their data.

## Key Concepts
- **LoRA의 정의** : LoRA는 대형 언어 모델을 효율적으로 fine-tuning하기 위한 기법으로, 모델의 원래 가중치를 고정하고 별도의 가중치를 추가하여 fine-tuning을 수행한다.
- **LoRA의 장점** : LoRA는 fine-tuning 과정에서 필요한 메모리와 계산 자원을 크게 줄여주어, 소규모 조직이나 개인 개발자가 대형 언어 모델을 특정 도메인에 맞게 fine-tuning할 수 있도록 한다.
- **LoRA의 적용** : LoRA는 다양한 대형 언어 모델에 적용할 수 있으며, 특히 다중 클라이언트가 서로 다른 애플리케이션을 위해 fine-tuned 모델을 필요로 할 때 유용하다.

## References
| URL 이름 | URL |
| --- | --- |
| Easily Train a Specialized LLM: PEFT, LoRA, QLoRA, LLaMA | https://cameronrwolfe.substack.com/p/easily-train-a-specialized-llm-peft |
| Mastering Low-Rank Adaptation (LoRA): Enhancing Large Language Models for Efficient Adaptation | https://www.datacamp.com/tutorial/mastering-low-rank-adaptation-lora-enhancing-large-language-models-for-efficient-adaptation |
| Understanding LLM Fine Tuning with LoRA (Low-Rank Adaptation) | https://www.run.ai/guides/generative-ai/lora-fine-tuning |
| A beginners guide to fine tuning LLM using LoRA | https://zohaib.me/a-beginners-guide-to-fine-tuning-llm-using-lora/ |
| What is low-rank adaptation (LoRA)? | https://bdtechtalks.com/2023/05/22/what-is-lora/ |