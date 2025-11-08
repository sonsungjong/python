
import threading

from pathlib import Path

import torch
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor, TextIteratorStreamer

MODEL_ID = "Qwen/Qwen3-VL-32B-Thinking"
DEVICE = "cuda:0"

def main():
    # 모델 로드 (한 번만)
    print("모델 로딩 중...")
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = AutoModelForVision2Seq.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map={"": DEVICE},
    )
    model.eval()
    print("모델 로딩 완료!\n")
    
    # 무한루프로 이미지 처리
    while True:
        # 이미지 경로 입력받기
        image_path_str = input("이미지 파일 경로를 입력하세요 (종료: q 또는 quit): ").strip()
        
        # 종료 조건
        if image_path_str.lower() in ['q', 'quit', 'exit']:
            print("프로그램을 종료합니다.")
            break
        
        # 빈 입력 처리
        if not image_path_str:
            print("경로를 입력해주세요.\n")
            continue
        
        image_path = Path(image_path_str)
        
        # 경로 검증
        if not image_path.exists():
            print(f"❌ 이미지 파일을 찾을 수 없습니다: {image_path}\n")
            continue
        
        try:
            image = Image.open(image_path).convert("RGB")
        except Exception as e:
            print(f"❌ 이미지 로드 실패: {e}\n")
            continue

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": "이미지에 있는 모든 텍스트를 추출해줘."},
                ],
            },
        ]

        inputs = processor.apply_chat_template(
            messages,
            add_generation_prompt=True,
            tokenize=True,
            return_dict=True,
            return_tensors="pt",
        )
        processed_inputs = {}
        for key, value in inputs.items():
            if isinstance(value, torch.Tensor):
                target_kwargs = {"device": DEVICE}
                if value.dtype.is_floating_point:
                    target_kwargs["dtype"] = torch.bfloat16
                processed_inputs[key] = value.to(**target_kwargs)
            else:
                processed_inputs[key] = value
        inputs = processed_inputs

        streamer = TextIteratorStreamer(
            tokenizer=processor.tokenizer,
            skip_prompt=True,
            skip_special_tokens=False,
        )

        pad_token_id = processor.tokenizer.pad_token_id or processor.tokenizer.eos_token_id

        generate_kwargs = {
            **inputs,
            "streamer": streamer,
            "max_new_tokens": 512,
            "pad_token_id": pad_token_id,
            "eos_token_id": processor.tokenizer.eos_token_id,
        }

        def _generate():
            with torch.inference_mode():
                model.generate(**generate_kwargs)

        print("\n모델 응답 스트리밍 중...\n")
        full_text = ""

        worker = threading.Thread(target=_generate)
        worker.start()

        for text in streamer:
            print(text, end="", flush=True)
            full_text += text

        worker.join()

        split_marker = "</think>\n\n"
        if split_marker in full_text:
            final_answer = full_text.split(split_marker, 1)[1].strip()
        else:
            final_answer = full_text.strip()

        final_answer = final_answer.replace("<|im_end|>", "").strip()

        print("\n" + "=" * 80)
        print("AI 최종 답변")
        print("=" * 80)
        print(final_answer)
        print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
