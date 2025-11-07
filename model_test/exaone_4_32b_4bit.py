# bitsandbytes (4bit/8bit)
# pip install bitsandbytes

from transformers import pipeline, TextIteratorStreamer, BitsAndBytesConfig
import torch
from threading import Thread
import sys

def main():
    model_id = "LGAI-EXAONE/EXAONE-4.0-32B"
    
    print("모델 로딩 중... (4bit 양자화)")
    
    # 4bit 양자화 설정
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.bfloat16
    )
    
    # 모델 로드 (한 번만) - 4bit 양자화 적용
    pipe = pipeline(
        "text-generation",
        model=model_id,
        model_kwargs={"quantization_config": bnb_config},
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    
    print("모델 로딩 완료!")
    print("=" * 80)
    print("대화를 시작합니다. 종료하려면 /bye 를 입력하세요.")
    print("=" * 80)
    
    # 대화 기록 저장 (사용자 질문과 AI 답변만)
    messages = []
    
    while True:
        # 사용자 입력
        user_input = input("\n[You] >>> ")
        
        # 종료 명령 체크
        if user_input.lower() in ['/bye']:
            print("\n대화를 종료합니다.")
            break
        
        if not user_input.strip():
            continue
        
        # 사용자 메시지 추가
        messages.append({"role": "user", "content": user_input})
        
        # 스트리밍 생성
        print("\n[AI] >>> ", end="", flush=True)
        
        # TextIteratorStreamer 설정
        streamer = TextIteratorStreamer(
            pipe.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )
        
        # 백그라운드에서 생성
        generation_kwargs = dict(
            text_inputs=messages,
            streamer=streamer,
            max_new_tokens=2048,
        )
        
        thread = Thread(target=pipe, kwargs=generation_kwargs)
        thread.start()
        
        # 스트리밍 출력 및 전체 응답 수집
        full_response = ""
        for new_text in streamer:
            print(new_text, end="", flush=True)
            full_response += new_text
        
        thread.join()
        print("\n")  # 줄바꿈
        
        # assistantfinal 이후의 답변만 추출
        answer_only = ""
        if 'assistantfinal' in full_response:
            split_pos = full_response.find('assistantfinal')
            answer_only = full_response[split_pos + len('assistantfinal'):].strip()
            
            # 답변 부분만 다시 정리해서 보여주기
            print("=" * 80)
            print("[AI 답변]")
            print("-" * 80)
            print(answer_only)
            print("=" * 80)
        else:
            # assistantfinal이 없으면 전체를 답변으로
            answer_only = full_response.strip()
        
        # 답변만 대화 기록에 추가 (생각은 제외)
        messages.append({"role": "assistant", "content": answer_only})

if __name__ == "__main__":
    main()
