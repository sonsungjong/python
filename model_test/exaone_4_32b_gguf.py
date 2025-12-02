from llama_cpp import Llama
import sys

def main():
    model_id = "LGAI-EXAONE/EXAONE-4.0-32B-GGUF"
    gguf_file = "EXAONE-4.0-32B-Q4_K_M.gguf"
    
    print("=" * 80)
    print("EXAONE 4.0 32B GGUF 대화형 모드")
    print("=" * 80)
    print(f"모델 로딩 중... ({gguf_file})")
    print("=" * 80)
    
    # GGUF 모델 로드
    try:
        # Jinja2ChatFormatter를 패치하여 continue 태그 지원
        from llama_cpp import llama_chat_format
        from jinja2 import nodes
        from jinja2.ext import Extension
        
        # Continue 태그를 무시하는 Jinja2 확장
        class ContinueExtension(Extension):
            tags = {'continue'}
            
            def parse(self, parser):
                lineno = next(parser.stream).lineno
                # continue를 빈 Output 노드로 변환
                return nodes.Output([nodes.TemplateData('', lineno=lineno)], lineno=lineno)
        
        # 기존 Jinja2ChatFormatter.__init__ 백업
        original_init = llama_chat_format.Jinja2ChatFormatter.__init__
        
        def patched_init(self, template, *args, **kwargs):
            # Jinja2 환경에 Continue 확장 추가
            from jinja2 import Environment
            
            # kwargs에서 eos_token과 bos_token 처리
            self.template = template
            self.eos_token = kwargs.get('eos_token', '')
            self.bos_token = kwargs.get('bos_token', '')
            
            try:
                self._environment = Environment(
                    extensions=[ContinueExtension],
                    trim_blocks=True,
                    lstrip_blocks=True
                )
                self._environment.globals.update({
                    'raise_exception': lambda msg: (_ for _ in ()).throw(Exception(msg)),
                    'strftime_now': lambda fmt: __import__('datetime').datetime.now().strftime(fmt)
                })
                self._template = self._environment.from_string(self.template)
            except Exception as e:
                print(f"⚠️  chat_template 파싱 실패, 기본 포맷 사용: {e}")
                self._template = None
        
        # __call__ 메서드도 패치
        from llama_cpp.llama_chat_format import ChatFormatterResponse
        
        original_call = llama_chat_format.Jinja2ChatFormatter.__call__
        
        def patched_call(self, *args, **kwargs):
            if not hasattr(self, '_template') or self._template is None:
                # 템플릿이 없으면 기본 포맷 사용
                messages = kwargs.get('messages', [])
                prompt = ""
                for msg in messages:
                    role = msg.get('role', '')
                    content = msg.get('content', '')
                    if role == 'system':
                        prompt += f"[|system|]\n{content}[|endofturn|]\n"
                    elif role == 'user':
                        prompt += f"[|user|]\n{content}[|endofturn|]\n"
                    elif role == 'assistant':
                        prompt += f"[|assistant|]\n{content}[|endofturn|]\n"
                prompt += "[|assistant|]\n"
                return ChatFormatterResponse(prompt=prompt, stop=['[|endofturn|]'])
            else:
                # 템플릿 사용
                try:
                    messages = kwargs.get('messages', [])
                    rendered = self._template.render(
                        messages=messages,
                        eos_token=self.eos_token,
                        bos_token=self.bos_token,
                        add_generation_prompt=kwargs.get('add_generation_prompt', True)
                    )
                    return ChatFormatterResponse(prompt=rendered, stop=['[|endofturn|]'])
                except Exception as e:
                    print(f"⚠️  템플릿 렌더링 실패: {e}")
                    # 기본 포맷으로 폴백
                    messages = kwargs.get('messages', [])
                    prompt = ""
                    for msg in messages:
                        role = msg.get('role', '')
                        content = msg.get('content', '')
                        if role == 'system':
                            prompt += f"[|system|]\n{content}[|endofturn|]\n"
                        elif role == 'user':
                            prompt += f"[|user|]\n{content}[|endofturn|]\n"
                        elif role == 'assistant':
                            prompt += f"[|assistant|]\n{content}[|endofturn|]\n"
                    prompt += "[|assistant|]\n"
                    return ChatFormatterResponse(prompt=prompt, stop=['[|endofturn|]'])
        
        # 패치 적용
        llama_chat_format.Jinja2ChatFormatter.__init__ = patched_init
        llama_chat_format.Jinja2ChatFormatter.__call__ = patched_call
        
        # 이제 모델 로드
        llm = Llama.from_pretrained(
            repo_id=model_id,
            filename=gguf_file,
            n_gpu_layers=-1,
            n_ctx=8192,
            verbose=False,
            n_threads=8,
        )
        
    except Exception as e:
        print(f"❌ 모델 로딩 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("모델 로딩 완료!")
    print("=" * 80)
    print("대화를 시작합니다. 종료하려면 /bye 를 입력하세요.")
    print("=" * 80)
    print("\n💡 팁:")
    print("  - EXAONE은 한국어, 영어, 스페인어를 지원합니다")
    print("  - 자연스러운 대화가 가능합니다")
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
        
        full_response = ""
        
        try:
            # create_chat_completion 사용
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
            if not full_response.strip():
                continue
        
        except Exception as e:
            print(f"\n\n❌ 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            messages.pop()  # 오류 발생 시 마지막 사용자 메시지 제거
            continue
        
        # 답변을 대화 기록에 추가
        answer_only = full_response.strip()
        if answer_only:
            messages.append({"role": "assistant", "content": answer_only})

if __name__ == "__main__":
    main()
