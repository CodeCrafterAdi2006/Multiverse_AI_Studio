# Skill: ML Model Quantization

## Purpose
To reduce the memory footprint and improve inference speed of Machine Learning models, particularly deep neural networks, by converting high-precision weights (e.g., FP32) to lower-precision representations (e.g., INT8) with minimal loss of accuracy.

## When to Use
- When deploying models to edge devices (mobile, IoT) with limited memory or compute
- When optimizing inference costs on cloud infrastructure
- When striving for real-time performance in computer vision or NLP tasks
- When the model size exceeds deployment constraints

## Procedure

### 1. Identify Quantization Strategy
Choose the appropriate quantization method based on your deployment needs:
- **Post-Training Quantization (PTQ)**: Applied after training. Easiest to implement. Good for general use cases.
- **Quantization-Aware Training (QAT)**: Simulates quantization during training. Results in higher accuracy, but requires retraining.

### 2. Post-Training Quantization (PyTorch Example)

**Dynamic Quantization** (Best for LSTM/RNN or Transformer models):
```python
import torch

# 1. Load your pre-trained model
model = MyTransformerModel()
model.load_state_dict(torch.load('model_fp32.pth'))
model.eval()

# 2. Apply dynamic quantization to specific layers (e.g., Linear layers)
quantized_model = torch.quantization.quantize_dynamic(
    model, {torch.nn.Linear}, dtype=torch.qint8
)

# 3. Save the quantized model
torch.save(quantized_model.state_dict(), 'model_int8.pth')
```

**Static Quantization** (Best for CNNs):
Requires a representative dataset to calibrate the activations.
```python
import torch

# 1. Prepare model for static quantization
model.eval()
model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
torch.quantization.prepare(model, inplace=True)

# 2. Calibrate with representative data
for data, _ in representative_dataloader:
    model(data)

# 3. Convert to quantized model
torch.quantization.convert(model, inplace=True)
```

### 3. Quantization-Aware Training (QAT)
If PTQ causes an unacceptable drop in accuracy, use QAT.

```python
import torch

# 1. Prepare model for QAT
model.train()
model.qconfig = torch.quantization.get_default_qat_qconfig('fbgemm')
torch.quantization.prepare_qat(model, inplace=True)

# 2. Fine-tune the model
for epoch in range(num_epochs):
    for data, target in train_dataloader:
        optimizer.zero_grad()
        output = model(data)
        loss = criterion(output, target)
        loss.backward()
        optimizer.step()

# 3. Convert to quantized model for inference
model.eval()
torch.quantization.convert(model, inplace=True)
```

## Best Practices
- Always benchmark accuracy before and after quantization.
- For LLMs, consider specialized quantization libraries like `bitsandbytes` (4-bit/8-bit) or formats like GGUF/AWQ.
- Use the appropriate backend (e.g., `fbgemm` for x86, `qnnpack` for ARM).