from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer

# 원본 모델 경로
model_path = "Qwen/Qwen3-Omni-30B-A3B-Instruct"
# 저장할 경로
quant_path = "./Qwen3-Omni-30B-A3B-Instruct-AWQ-4bit"

# 양자화 설정
quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,               # 4bit
    "version": "GEMM"         # 또는 "GEMV"
}

# 모델 & 토크나이저 로드
model = AutoAWQForCausalLM.from_pretrained(
    model_path,
    trust_remote_code=True,      # Qwen 커스텀 코드 허용
)
tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)

# 양자화 실행 (캘리브레이션 데이터 필요)
model.quantize(tokenizer, quant_config=quant_config)

# 저장
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)

print(f"AWQ 양자화 완료: {quant_path}")