# PaddleOCR-VL 로 먼저 텍스트를 추출한다음
# 필요에 따라 유형을 파악해서 프롬프트를 구성하고
# PaddleOCR-VL 추출한 텍스트를 힌트로 넘겨서 Qwen3-VL-30B-4bit 와 Qwen3-VL-32B-4bit 를 실행하고 결과를 비교한다
# 결과 비교헀는데 동일하지 않으면 마지막으로 Qwen3-VL-32B-Thinking 으로 실행한다

from transformers import AutoProcessor, AutoModelForVision2Seq

processor = AutoProcessor.from_pretrained("Qwen/Qwen3-VL-32B-Thinking")
model = AutoModelForVision2Seq.from_pretrained("Qwen/Qwen3-VL-32B-Thinking")
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image", "url": "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/p-blog/candy.JPG"},
            {"type": "text", "text": "What animal is on the candy?"}
        ]
    },
]
inputs = processor.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=40)
print(processor.decode(outputs[0][inputs["input_ids"].shape[-1]:]))