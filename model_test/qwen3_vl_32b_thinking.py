"""
PaddleOCR-VL 로 먼저 텍스트를 추출하고 결과가 다르면 최종적으로
Qwen3-VL-32B-Thinking 모델을 사용해 답변을 생성하는 테스트 스크립트.
"""

import threading

from pathlib import Path

import torch
from PIL import Image
from transformers import AutoModelForVision2Seq, AutoProcessor, TextIteratorStreamer

MODEL_ID = "Qwen/Qwen3-VL-32B-Thinking"
DEVICE = "cuda:0"
LOCAL_IMAGE_PATH = Path("/home/user/사진/스크린샷/스크린샷 2025-11-01 01-04-47.png")


def main():
    processor = AutoProcessor.from_pretrained(MODEL_ID)
    model = AutoModelForVision2Seq.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        device_map={"": DEVICE},
    )
    model.eval()

    if not LOCAL_IMAGE_PATH.exists():
        raise FileNotFoundError(f"이미지 파일을 찾을 수 없습니다: {LOCAL_IMAGE_PATH}")

    image = Image.open(LOCAL_IMAGE_PATH).convert("RGB")

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

    print("모델 응답 스트리밍 중...\n")
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
    print("=" * 80)


if __name__ == "__main__":
    main()
