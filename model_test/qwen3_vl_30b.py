# pip install transformers>=4.57.0
from transformers import Qwen3VLMoeForConditionalGeneration, AutoProcessor, TextIteratorStreamer
import torch
from pathlib import Path
from PIL import Image
from threading import Thread

def main():
    model_id = "Qwen/Qwen3-VL-30B-A3B-Instruct"
    
    print("모델 로딩 중...")
    
    # Flash Attention 2 설치: pip install flash-attn --no-build-isolation
    # Flash Attention 2 사용 (권장 - 메모리 절약 및 속도 향상)
    try:
        model = Qwen3VLMoeForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype="auto",
            attn_implementation="flash_attention_2",
            device_map="auto",
        )
        print("✅ SUCCESS: Flash Attention 2 활성화")
    except:
        # Flash Attention 없을 경우 예외처리로 기본 모드 
        model = Qwen3VLMoeForConditionalGeneration.from_pretrained(
            model_id,
            torch_dtype="auto",
            device_map="auto"
        )
        print("⚠️  WARNING: Flash Attention 2 없이 기본 모드로 로드")
    
    processor = AutoProcessor.from_pretrained(model_id)
    
    print("✅ 모델 로딩 완료!\n")
    
    # 무한 루프로 여러 이미지 처리
    while True:
        print("=" * 80)
        image_path_str = input("이미지 파일 경로를 입력하세요 (종료: q 또는 quit): ").strip()
        
        # 종료 조건
        if image_path_str.lower() in ['q', 'quit', 'exit']:
            print("프로그램을 종료합니다.")
            break
        
        # 빈 입력 체크
        if not image_path_str:
            print("경로를 입력해주세요.\n")
            continue
        
        # 경로 검증
        image_path = Path(image_path_str)
        if not image_path.exists():
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}\n")
            continue
        
        # 이미지 로드
        try:
            image = Image.open(image_path).convert("RGB")
            print(f"✅ 이미지 로드 완료: {image_path}")
        except Exception as e:
            print(f"❌ 이미지 로드 실패: {e}\n")
            continue
        
        # 프롬프트 설정
        prompt = input("프롬프트 (기본: 이미지에 있는 모든 텍스트를 추출해줘): ").strip()
        if not prompt:
            prompt = "이미지에 있는 모든 텍스트를 추출해줘."
        
        # 메시지 구성
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        
        print("\n🚀 텍스트 추출 중...\n")
        print("=" * 80)
        
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
        
        # Streamer 생성 (스트리밍 출력)
        streamer = TextIteratorStreamer(
            processor.tokenizer,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=False
        )
        
        # 생성 파라미터
        generation_kwargs = {
            **inputs,
            "max_new_tokens": 512,
            "streamer": streamer,
            "do_sample": False,  # greedy decoding
        }
        
        # 백그라운드 스레드로 생성
        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()
        
        # 실시간 스트리밍 출력
        print("📝 답변: ", end="", flush=True)
        for text in streamer:
            print(text, end="", flush=True)
        
        thread.join()
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()
