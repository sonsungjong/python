# pip install transformers>=4.57.0
from transformers import Qwen3VLMoeForConditionalGeneration, AutoProcessor
import torch

def main():
    model_id = "Qwen/Qwen3-VL-30B-A3B-Instruct"
    
    print("모델 로딩 중...")
    
    # Flash Attention 2 설치: pip install flash-attn --no-build-isolation
    # Flash Attention 2 사용 (권장 - 메모리 절약 및 속도 향상)
    try:
        model = Qwen3VLMoeForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
            attn_implementation="flash_attention_2",
            device_map="auto",
        )
        print("SUCCESS: Flash Attention 2 활성화")
    except:
        # Flash Attention 없을 경우 예외처리로 기본 모드
        model = Qwen3VLMoeForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto"
        )
        print("ERROR: 기본 모드로 로드 ==> pip install flash-attn --no-build-isolation")
    
    processor = AutoProcessor.from_pretrained(model_id)
    
    print("모델 로딩 완료!\n")
    
    # 기본 이미지 설정
    image_url = "https://raw.githubusercontent.com/sonsungjong/resources/main/Gemini Board.png"
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image_url},
                {"type": "text", "text": "이미지에 적힌 글자를 읽어줘."},
            ],
        }
    ]
    
    print("생성 중...\n")
    
    # Preparation for inference
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt"
    )
    
    # GPU로 이동
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    # Inference: Generation of the output
    generated_ids = model.generate(**inputs, max_new_tokens=512)
    generated_ids_trimmed = [
        out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs["input_ids"], generated_ids)
    ]
    output_text = processor.batch_decode(
        generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
    )
    
    print("=" * 80)
    print("답변:")
    print("=" * 80)
    print(output_text[0])
    print("=" * 80)

if __name__ == "__main__":
    main()
