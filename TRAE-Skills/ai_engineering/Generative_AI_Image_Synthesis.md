# Skill: Generative AI Image Synthesis

## Purpose
To create and integrate generative image AI models (Stable Diffusion, DALL-E, Midjourney API) into applications for generating, editing, and manipulating images programmatically.

## When to Use
- When building applications that require on-demand image generation from text prompts
- For creating custom image editing tools using AI inpainting/outpainting
- When implementing AI-powered design tools for creative industries
- For generating synthetic datasets for computer vision tasks

## Procedure

### 1. Stable Diffusion Integration (Hugging Face)
Use the Hugging Face Diffusers library for local Stable Diffusion generation.

```python
from diffusers import StableDiffusionPipeline
import torch

model_id = "runwayml/stable-diffusion-v1-5"
pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to("cuda")

prompt = "A majestic lion standing on a cliff at sunset, photorealistic"
image = pipe(prompt).images[0]
image.save("lion_sunset.png")
```

### 2. OpenAI DALL-E API Integration
Use OpenAI's API for cloud-based image generation.

```javascript
import OpenAI from 'openai';

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function generateImage(prompt) {
  const response = await openai.images.generate({
    model: 'dall-e-3',
    prompt: prompt,
    n: 1,
    size: '1024x1024',
    quality: 'standard',
  });
  return response.data[0].url;
}
```

### 3. Inpainting for Image Editing
Modify specific regions of existing images.

```python
from diffusers import StableDiffusionInpaintPipeline
from PIL import Image
import torch

pipe = StableDiffusionInpaintPipeline.from_pretrained(
    "runwayml/stable-diffusion-inpainting",
    torch_dtype=torch.float16
).to("cuda")

image = Image.open("original_image.jpg")
mask = Image.open("mask_image.png")

prompt = "A cute dog sitting on the couch"
result = pipe(prompt=prompt, image=image, mask_image=mask).images[0]
result.save("edited_image.jpg")
```

### 4. Image-to-Image Translation
Transform existing images based on text prompts.

```python
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image
import torch

pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")

init_image = Image.open("sketch.jpg").convert("RGB")
prompt = "A realistic watercolor painting of a mountain landscape"

result = pipe(prompt=prompt, image=init_image, strength=0.75, guidance_scale=7.5).images[0]
result.save("watercolor_mountain.jpg")
```

## Best Practices
- **Prompt Engineering**: Be specific about style, lighting, composition, and artists for better results
- **Memory Management**: Use float16 and model quantization to reduce GPU memory usage
- **Caching**: Cache frequently used generated images to reduce API costs
- **Content Moderation**: Implement safety filters to prevent generation of inappropriate content
- **Rate Limiting**: Respect API rate limits and implement retry logic with exponential backoff
