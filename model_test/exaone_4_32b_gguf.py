from llama_cpp import Llama
import sys

def main():
    model_id = "LGAI-EXAONE/EXAONE-4.0-32B-GGUF"
    # 양자화 옵션:
    # - Q4_K_M: 품질과 속도의 균형 (권장)
    # - Q5_K_M: 더 높은 품질
    # - Q6_K: 매우 높은 품질
    # - Q8_0: 최고 품질
    # - IQ4_XS: 최소 크기
    gguf_file = "EXAONE-4.0-32B-Q4_K_M.gguf"
    
    print("=" * 80)
    print("EXAONE 4.0 32B GGUF 대화형 모드")
    print("=" * 80)
    print(f"모델 로딩 중... ({gguf_file})")
    print("=" * 80)
    
    # GGUF 모델 로드
    llm = Llama.from_pretrained(
        repo_id=model_id,
        filename=gguf_file,
        n_gpu_layers=-1,      # 모든 레이어를 GPU로
        n_ctx=8192,           # 컨텍스트 길이 (EXAONE은 131K까지 가능하지만 메모리 고려)
        verbose=False,         # 로딩 정보 표시
        n_threads=8,          # CPU 스레드 수
    )
    
    print("\n" + "=" * 80)
    print("모델 로딩 완료!")
    print("=" * 80)
    print("대화를 시작합니다. 종료하려면 /bye 를 입력하세요.")
    print("=" * 80)
    print("\n💡 팁:")
    print("  - EXAONE은 한국어, 영어, 스페인어를 지원합니다")
    print("  - Reasoning mode와 Non-reasoning mode를 지원합니다")
    print("  - 시스템 프롬프트에서 'Reasoning: high'로 추론 레벨 조정 가능")
    print("=" * 80)
    
    # 대화 기록 저장
    messages = []
    
    while True:
        # 사용자 입력
        user_input = input("\n[You] >>> ")
        
        # 종료 명령 체크
        if user_input.lower() in ['/bye', 'quit', 'exit', 'q']:
            print("\n대화를 종료합니다.")
            break
        
        if not user_input.strip():
            continue
        
        # 사용자 메시지 추가
        messages.append({"role": "user", "content": user_input})
        
        # 스트리밍 생성
        print("\n[EXAONE] >>> ", end="", flush=True)
        
        # 스트리밍 출력 및 전체 응답 수집
        full_response = ""
        
        try:
            # llama-cpp-python의 create_chat_completion 사용
            response = llm.create_chat_completion(
                messages=messages,
                max_tokens=2048,
                stream=True,
                temperature=0.7,
                top_p=0.9,
            )
            
            for chunk in response:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    if 'content' in delta:
                        token = delta['content']
                        print(token, end="", flush=True)
                        full_response += token
            
            print("\n")  # 줄바꿈
            
        except KeyboardInterrupt:
            print("\n\n⚠️ 생성이 중단되었습니다.")
            # 중단된 경우에도 지금까지의 응답 사용
            if not full_response.strip():
                continue
        
        except Exception as e:
            print(f"\n\n❌ 오류 발생: {e}")
            messages.pop()  # 오류 발생 시 마지막 사용자 메시지 제거
            continue
        
        # EXAONE은 특별한 구분자가 없으므로 전체를 답변으로 저장
        answer_only = full_response.strip()
        
        # 답변을 대화 기록에 추가
        if answer_only:
            messages.append({"role": "assistant", "content": answer_only})

if __name__ == "__main__":
    main()
