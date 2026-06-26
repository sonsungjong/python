# pat-jj/harness-1
# https://huggingface.co/pat-jj/harness-1

# ----------------------------------------------------------------------
"""
vllm 설치 및 빌드 가이드

"""

# 모델 다운로드:
'''
hf download pat-jj/harness-1
'''
# vllm 서버 실행:
'''
vllm-openai \
  --model ~/.cache/huggingface/hub/models--pat-jj--harness-1/snapshots/*/harness-1 \

'''
# 서버 종료:
# Ctrl+C 또는
# pkill -f llama-server
# 또는 PID로 종료: kill $(pgrep -f llama-server)

from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("pat-jj/harness-1")
model = AutoModelForCausalLM.from_pretrained("pat-jj/harness-1")
messages = [
    {"role": "user", "content": "넌 누구냐?"},
]
inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
).to(model.device)

outputs = model.generate(**inputs, max_new_tokens=4096)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))