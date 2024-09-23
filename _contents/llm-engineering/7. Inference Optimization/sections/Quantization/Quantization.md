# **Quantization in LLM**

## **Summary**
Quantization in Large Language Models (LLMs) is a model compression technique aimed at reducing the size and computational requirements of these models by converting their weights and activations from high-precision data types to lower-precision ones. This process involves mapping continuous values to a smaller set of discrete values, which significantly decreases the model's memory footprint and computational needs, making it more efficient and accessible, particularly for deployment on resource-constrained devices. Various quantization techniques, such as linear quantization, post-training quantization (PTQ), and quantization-aware training (QAT), are employed to achieve this goal while minimizing the impact on model performance.

## **Key Concepts**
- **Quantization**: A technique used to reduce the precision of model weights and activations, converting them from high-precision data types (e.g., FP32) to lower-precision ones (e.g., INT8).
- **Linear Quantization**: A method that maps the range of floating-point values to a range of fixed-point values evenly, using a scale factor and zero-point to ensure numerical accuracy.
- **Post-Training Quantization (PTQ)**: A technique where quantization is performed after the model has been trained, aiming to find a simpler version of the weights that still yields good results.
- **Quantization-Aware Training (QAT)**: A method where quantization is integrated into the training process, allowing the model to learn to be robust to quantization noise.
- **Calibration**: The process of selecting the optimal range for quantization, which includes techniques such as choosing a percentile of the input range, optimizing the mean squared error (MSE), and minimizing entropy (KL-divergence).

## **References**
| URL Name | URL |
| --- | --- |
| A Visual Guide to Quantization | https://www.maartengrootendorst.com/blog/quantization/ |
| LLM Quantization: Techniques, Advantages, and Models | https://www.tensorops.ai/post/what-are-quantized-llms |
| Quantization for Large Language Models (LLMs): Reduce AI Model Size | https://www.datacamp.com/tutorial/quantization-for-large-language-models |
| The Ultimate Handbook for LLM Quantization | https://towardsdatascience.com/the-ultimate-handbook-for-llm-quantization-88bb7cb0d9d7 |
| A Guide to Quantization in LLMs | https://symbl.ai/developers/blog/a-guide-to-quantization-in-llms/ |