"""K-EXAONE 2.5 대화형 API 예제.

설치: python -m pip install requests
실행: python model_test/k_exaone_25_api.py
문서: https://docs.exaone.ai/ko/docs/k-exaone-2.5
"""

import json
import time

import requests


# ========================= 변경할 설정 =========================
API_KEY = "sk-EwzB3gwUGEoOkpSG7x4iyhcldmlviDY8TdfGEjRuKG4"
API_URL = "https://api.exaone.ai/v1/chat/completions"
MODEL = "k-exaone_v2.5"
SYSTEM_PROMPT = "당신은 친절한 AI 도우미입니다. 사용자의 질문에 한국어로 답하세요."

STREAM = True             # True: 생성되는 대로 출력 / False: 완성 후 한 번에 출력
# 이 API는 enable_thinking=True로 고정되어 추론 연산 자체를 끌 수 없습니다.
SHOW_THINKING = True     # True: 추론 과정 표시 / False: 숨김 (추론은 계속 수행)
REASONING_EFFORT = "high"  # 추론 강도: "low"(빠른 응답), "high", "max"

MAX_TOKENS = 32768         # 추론 + 최종 답변을 합친 최대 출력 토큰 수
TEMPERATURE = 1.0         # 답변의 무작위성. 공식 권장값: 1.0
TOP_P = 0.95              # 누적 확률 기준 샘플링. 공식 권장값: 0.95
TOP_K = -1                # 상위 k개 후보 사용. -1이면 필터링 비활성화
PRESENCE_PENALTY = 0.0    # 반복 억제 강도: -2.0 ~ 2.0
TIMEOUT_SECONDS = 180     # 서버 응답을 기다리는 제한 시간(초)

KEEP_HISTORY = True       # True: 이전 대화를 포함 / False: 매번 독립된 질문
PRESERVE_THINKING = False  # 멀티턴에서 이전 assistant의 추론도 보존
SHOW_USAGE = True         # 토큰 사용량과 응답 시간 표시 여부
# ===============================================================


def new_messages() -> list[dict[str, str]]:
    """시스템 프롬프트로 새 대화를 시작합니다."""
    return [{"role": "system", "content": SYSTEM_PROMPT}] if SYSTEM_PROMPT else []


def read_stream(response: requests.Response) -> dict:
    """SSE 응답을 즉시 출력하면서 최종 답변, 추론, 사용량을 모읍니다."""
    answer_parts = []
    thinking_parts = []
    usage = {}
    finish_reason = None
    displayed_section = None
    completed = False
    response.encoding = "utf-8"  # text/event-stream의 한글이 깨지지 않도록 지정

    # 작은 청크로 읽어 requests의 버퍼에 출력이 지연되지 않게 합니다.
    for line in response.iter_lines(chunk_size=1, decode_unicode=True):
        if not line or not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            completed = True
            break

        chunk = json.loads(data)
        if chunk.get("error"):
            detail = json.dumps(chunk["error"], ensure_ascii=False)
            raise RuntimeError(detail.replace(API_KEY, "[API_KEY]")[:1000])
        if chunk.get("usage") is not None:
            usage = chunk["usage"]

        # 사용량만 있는 마지막 청크는 choices가 빈 배열일 수 있습니다.
        for choice in chunk.get("choices") or []:
            if choice.get("index", 0) != 0:
                continue
            if choice.get("finish_reason") is not None:
                finish_reason = choice["finish_reason"]
            delta = choice.get("delta") or {}
            thinking = delta.get("reasoning_content") or ""
            answer = delta.get("content") or ""

            if thinking:
                thinking_parts.append(thinking)
                if SHOW_THINKING:
                    if displayed_section != "thinking":
                        print("\n[Thinking]", flush=True)
                        displayed_section = "thinking"
                    print(thinking, end="", flush=True)
            if answer:
                answer_parts.append(answer)
                if displayed_section != "answer":
                    print("\n[AI]", flush=True)
                    displayed_section = "answer"
                print(answer, end="", flush=True)

    if displayed_section is not None:
        print(flush=True)
    if not completed:
        raise RuntimeError("스트리밍이 완료 전에 끊겼습니다. 다시 요청하세요.")

    # 두 응답 모드를 같은 형태로 반환해 대화 기록과 사용량 처리를 공유합니다.
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": "".join(answer_parts),
                "reasoning_content": "".join(thinking_parts),
            },
            "finish_reason": finish_reason,
        }],
        "usage": usage,
    }


def call_api(messages: list[dict[str, str]]) -> dict:
    """STREAM 설정에 맞춰 요청하고 Chat Completion 형태로 반환합니다."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": MAX_TOKENS,
        "stream": STREAM,
        "temperature": TEMPERATURE,
        "top_p": TOP_P,
        "top_k": TOP_K,
        "presence_penalty": PRESENCE_PENALTY,
        "reasoning_effort": REASONING_EFFORT,
        "chat_template_kwargs": {"preserve_thinking": PRESERVE_THINKING},
    }
    if STREAM:
        payload["stream_options"] = {"include_usage": SHOW_USAGE}
    headers = {
        "Authorization": f"Bearer {API_KEY.strip()}",
        "Content-Type": "application/json",
    }

    with requests.post(
        API_URL,
        headers=headers,
        json=payload,
        stream=STREAM,
        timeout=(10, TIMEOUT_SECONDS),
    ) as response:
        if not response.ok:
            try:
                body = response.json()
                error = body.get("error", body) if isinstance(body, dict) else body
                detail = error.get("message", error) if isinstance(error, dict) else error
                if not isinstance(detail, str):
                    detail = json.dumps(detail, ensure_ascii=False)
            except ValueError:
                detail = response.text
            # 서버 오류 메시지에 키가 포함되더라도 콘솔에 노출하지 않습니다.
            detail = detail.replace(API_KEY, "[API_KEY]")[:1000]
            raise RuntimeError(f"HTTP {response.status_code}: {detail}")

        result = read_stream(response) if STREAM else response.json()

    if not isinstance(result, dict) or not result.get("choices"):
        raise RuntimeError("API 응답에 choices가 없습니다. 응답 형식을 확인하세요.")
    return result


def main() -> None:
    if not API_KEY.strip():
        print("코드 상단의 API_KEY에 EXAONE API 키를 입력하세요.")
        return
    if REASONING_EFFORT not in {"low", "high", "max"}:
        print('REASONING_EFFORT는 "low", "high", "max" 중 하나로 설정하세요.')
        return

    print(f"K-EXAONE 2.5 | 모델: {MODEL} | 추론 강도: {REASONING_EFFORT}")
    print(f"스트리밍: {'ON' if STREAM else 'OFF'} | Thinking 표시: {'ON' if SHOW_THINKING else 'OFF'}")
    print("이 API는 추론 연산을 항상 수행합니다. SHOW_THINKING은 화면 표시만 바꿉니다.")
    print("질문을 입력하세요. /clear: 대화 초기화, /exit: 종료")
    messages = new_messages()

    while True:
        try:
            user_input = input("\n[You] >>> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n대화를 종료합니다.")
            break

        if user_input.lower() in {"/exit", "/bye", "exit", "quit"}:
            print("대화를 종료합니다.")
            break
        if user_input.lower() == "/clear":
            messages = new_messages()
            print("대화 기록을 초기화했습니다.")
            continue
        if not user_input:
            continue

        # 요청이 실패하면 기존 대화에 이번 질문을 남기지 않습니다.
        request_messages = (messages if KEEP_HISTORY else new_messages()) + [
            {"role": "user", "content": user_input}
        ]
        print("응답 생성 중...", flush=True)
        started_at = time.perf_counter()

        try:
            result = call_api(request_messages)
        except requests.Timeout:
            print(f"\n응답 시간 초과: TIMEOUT_SECONDS({TIMEOUT_SECONDS})를 늘려보세요.")
            continue
        except requests.ConnectionError:
            print("\n연결 실패: 인터넷 연결 및 API_URL을 확인하세요.")
            continue
        except (requests.RequestException, ValueError, RuntimeError) as error:
            print(f"\n요청 실패: {error}")
            continue
        except KeyboardInterrupt:
            print("\n대화를 종료합니다.")
            break

        elapsed = time.perf_counter() - started_at
        choice = result["choices"][0]
        message = choice["message"]
        answer = (message.get("content") or "").strip()
        reasoning = (message.get("reasoning_content") or "").strip()

        # 스트리밍 모드에서는 read_stream()에서 이미 출력했습니다.
        if not STREAM:
            if SHOW_THINKING and reasoning:
                print(f"\n[Thinking]\n{reasoning}")
            print(f"\n[AI]\n{answer or '(최종 답변이 반환되지 않았습니다.)'}")
        elif not answer:
            print("\n[AI]\n(최종 답변이 반환되지 않았습니다.)")

        if choice.get("finish_reason") == "length":
            print(
                "\n[안내] 출력 토큰 한도에 도달했습니다. "
                "MAX_TOKENS에는 추론 토큰도 포함되므로 값을 늘려보세요."
            )

        if SHOW_USAGE:
            usage = result.get("usage") or {}
            print(
                f"\n[사용량] 입력 {usage.get('prompt_tokens', '?')} | "
                f"출력 {usage.get('completion_tokens', '?')} "
                f"(추론 {usage.get('reasoning_tokens', '?')}) | "
                f"전체 {usage.get('total_tokens', '?')} 토큰 | {elapsed:.2f}초"
            )

        if KEEP_HISTORY and answer:
            assistant_message = {"role": "assistant", "content": answer}
            if PRESERVE_THINKING and reasoning:
                assistant_message["reasoning_content"] = reasoning
            messages = request_messages + [assistant_message]


if __name__ == "__main__":
    main()
