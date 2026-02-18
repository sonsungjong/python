from llama_cpp import Llama
import sys

def main():
    model_id = "unsloth/gpt-oss-120b-GGUF"
    # Q4_K_M: 품질과 속도의 균형 (약 70GB, 2개 파일)
    # Q8_0: 최고 품질 (약 120GB, 2개 파일)
    # Q2_K: 가장 작은 크기 (약 45GB, 2개 파일)
    gguf_file = "Q4_K_M/gpt-oss-120b-Q4_K_M-00001-of-00002.gguf"
    
    print(f"모델 로딩 중... ({gguf_file})")
    
    # GGUF 모델 로드
    llm = Llama.from_pretrained(
        repo_id=model_id,
        filename=gguf_file,
        n_gpu_layers=-1,  # 모든 레이어를 GPU로
        n_ctx=131072,       # 컨텍스트 길이
        verbose=True       # 로딩 정보 표시
    )
    
    print("=" * 80)
    print("모델 로딩 완료! 종료하려면 /bye 를 입력하세요.")
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
        
        # 스트리밍 출력 및 전체 응답 수집
        full_response = ""
        
        # llama-cpp-python의 create_chat_completion 사용
        response = llm.create_chat_completion(
            messages=messages,
            max_tokens=4096,
            temperature=0.1,           # 다양성 추가
            repeat_penalty=1.1,        # 반복 억제
            top_p=0.9,                 # 더 나은 샘플링
            stream=True
        )
        
        for chunk in response:
            if 'choices' in chunk and len(chunk['choices']) > 0:
                delta = chunk['choices'][0].get('delta', {})
                if 'content' in delta:
                    token = delta['content']
                    print(token, end="", flush=True)
                    full_response += token
        
        print("\n")  # 줄바꿈
        
        # GGUF 모델의 특수 토큰 처리
        # <|channel|>final<|message|> 이후의 내용이 최종 답변
        answer_only = ""
        
        # 여러 패턴 시도
        if '<|channel|>final<|message|>' in full_response:
            # GGUF 형식: <|channel|>final<|message|>답변내용
            split_pos = full_response.find('<|channel|>final<|message|>')
            answer_only = full_response[split_pos + len('<|channel|>final<|message|>'):].strip()
        elif 'assistantfinal' in full_response:
            # transformers 형식: assistantfinal답변내용
            split_pos = full_response.find('assistantfinal')
            answer_only = full_response[split_pos + len('assistantfinal'):].strip()
        else:
            # 패턴이 없으면 전체를 답변으로
            answer_only = full_response.strip()
        
        # <|end|> 같은 특수 토큰 제거
        answer_only = answer_only.replace('<|end|>', '').strip()
        
        # 답변 부분만 다시 정리해서 보여주기
        if '<|channel|>final<|message|>' in full_response or 'assistantfinal' in full_response:
            print("=" * 80)
            print("[AI 답변]")
            print("-" * 80)
            print(answer_only)
            print("=" * 80)
        
        # 답변만 대화 기록에 추가 (생각은 제외)
        messages.append({"role": "assistant", "content": answer_only})

if __name__ == "__main__":
    main()
