# pip install -U transformers librosa accelerate
import os
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image

MODEL_ID = "google/gemma-4-31B-it"

# Load model
processor = AutoProcessor.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype="auto",
    # dtype="auto",
    device_map="auto"
)

# Prompt - add image before text
IMAGE_PATH = "~/source/python312/python/model_test/ocr/삼성종합상사^0001.png"
image = Image.open(os.path.expanduser(IMAGE_PATH))

messages = [
    {
        "role": "user", 
        "content": [
            #{"type": "image", "url": "https://raw.githubusercontent.com/google-gemma/cookbook/refs/heads/main/Demos/sample-data/GoldenGate.png"},
            #{"type": "text", "text": "What is shown in this image?"}
            {"type": "image", "image": image},
            {"type": "text", "text": "Extract all text from this image exactly as it appears. Preserve any table structure or layout as much as possible."}
        ]
    }
]

# Process input
inputs = processor.apply_chat_template(
    messages,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
    add_generation_prompt=True,
).to(model.device)
input_len = inputs["input_ids"].shape[-1]

# Generate output
outputs = model.generate(**inputs, max_new_tokens=512)
response = processor.decode(outputs[0][input_len:], skip_special_tokens=False)

# Print output
print(response)