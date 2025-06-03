from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch

# model_id = "google/gemma-3-4b-it"
# save_path = "./gemma3_model"  # 저장할 로컬 경로

# FP16 또는 기본 형식으로 모델 다운로드
# model = AutoModelForCausalLM.from_pretrained(
#     model_id,
#     device_map={"": "cuda"},
#     torch_dtype=torch.bfloat16
# )

# 토크나이저 로딩
# tokenizer = AutoTokenizer.from_pretrained(model_id)

# 특정 경로에 저장
# model.save_pretrained(save_path)
# tokenizer.save_pretrained(save_path)


pipe = pipeline(
    "image-text-to-text",
    model="google/gemma-3-4b-it",
    device="cuda",
    torch_dtype=torch.bfloat16
)

messages = [
    {
        "role": "system",
        "content": [{"type": "text", "text": "You are a helpful assistant."}]
    },
    {
        "role": "user",
        "content": [
            {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG"},
            {"type": "text", "text": "캔디가 몇개 있어?"}
        ]
    }
]

output = pipe(text=messages, max_new_tokens=200)
print(output[0]["generated_text"][-1]["content"])