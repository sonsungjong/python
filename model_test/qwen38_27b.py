"""Qwen3.8-27B 과 비교테스트

실행:
  python model_test/qwen38_27b.py                    # EXAONE 현재 설정 vs Qwen OFF
  python model_test/qwen38_27b.py --qwen-thinking    # EXAONE 현재 설정 vs Qwen ON
  python model_test/qwen38_27b.py --qwen-only --qwen-thinking

기본 실행은 콘솔에만 출력합니다. 파일 저장이 필요할 때만 --save를 추가하세요.

[사용예시]

curl -NsS     http://10.240.1.11:8000/v1/chat/completions     -H 'Content-Type: application/json'     -d     '{
  "model": "/models/Qwen3.8-27B",
  "messages": [
    {
      "role": "user",
      "content": "안녕"
    }
  ],
  "stream": true,
  "max_tokens": 32768,
  "chat_template_kwargs": {
    "enable_thinking": false
  }
}'

"""

import concurrent.futures
import hashlib
import importlib.util
import json
import statistics
import sys
import threading
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


# ========================= 비교 설정 =========================
QWEN_API_URL = "http://10.240.1.11:8000/v1/chat/completions"
QWEN_MODEL = "/models/Qwen3.8-27B"
QWEN_ENABLE_THINKING = False  # 사용자가 제공한 curl과 동일
MAX_TOKENS = 32768           # 두 모델에 같은 출력 예산 적용
TEMPERATURE = 1.0
TOP_P = 0.95
TOP_K = -1
PRESENCE_PENALTY = 0.0
CONNECT_TIMEOUT_SECONDS = 10
READ_TIMEOUT_SECONDS = 180
ROOT = Path(__file__).resolve().parent
EXAONE_SOURCE = ROOT / "k_exaone_25_api.py"  # API 키와 추론 강도를 이 파일에서 읽음
# =============================================================


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def request_stream(session, profile, messages):
    """같은 SSE 수신 코드로 답변, 추론량, 첫 출력 및 첫 답변 시간을 측정합니다."""
    payload = {
        "model": profile["model"], "messages": messages,
        "stream": True, "stream_options": {"include_usage": True},
        "max_tokens": MAX_TOKENS, "temperature": TEMPERATURE, "top_p": TOP_P,
        "top_k": TOP_K, "presence_penalty": PRESENCE_PENALTY,
        **profile["extra_parameters"],
    }
    headers = {"Content-Type": "application/json"}
    # EXAONE 키는 EXAONE 요청에만 붙이고 로컬 Qwen 서버에는 보내지 않습니다.
    if profile.get("api_key"):
        headers["Authorization"] = "Bearer " + profile["api_key"].strip()
    started_at = time.perf_counter()
    answer_parts, thinking_parts = [], []
    first_output = first_answer = None
    usage, finish_reason, served_model = {}, None, None
    completed = False
    with session.post(profile["url"], headers=headers, json=payload, stream=True,
                      timeout=(CONNECT_TIMEOUT_SECONDS, READ_TIMEOUT_SECONDS)) as response:
        if not response.ok:
            raise RuntimeError(f"HTTP {response.status_code}: {response.text[:1500]}")
        response.encoding = "utf-8"
        for line in response.iter_lines(chunk_size=1, decode_unicode=True):
            if not line or not line.startswith("data:"):
                continue
            raw = line[5:].strip()
            if raw == "[DONE]":
                completed = True
                break
            chunk = json.loads(raw)
            if chunk.get("error"):
                raise RuntimeError(json.dumps(chunk["error"], ensure_ascii=False))
            served_model = chunk.get("model") or served_model
            if chunk.get("usage") is not None:
                usage = chunk["usage"]
            for choice in chunk.get("choices") or []:
                if choice.get("index", 0) != 0:
                    continue
                finish_reason = choice.get("finish_reason") or finish_reason
                delta = choice.get("delta") or {}
                thinking = delta.get("reasoning_content") or delta.get("reasoning") or ""
                answer = delta.get("content") or ""
                if thinking.strip() or answer.strip():
                    elapsed = time.perf_counter() - started_at
                    if first_output is None:
                        first_output = elapsed
                    if answer.strip() and first_answer is None:
                        first_answer = elapsed
                thinking_parts.append(thinking)
                answer_parts.append(answer)
    if not completed:
        raise RuntimeError("SSE 응답이 [DONE] 전에 중단됨")
    elapsed = time.perf_counter() - started_at
    reasoning_tokens = usage.get("reasoning_tokens")
    if reasoning_tokens is None:
        reasoning_tokens = (usage.get("completion_tokens_details") or {}).get("reasoning_tokens")
    normalized_usage = {
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"), "reasoning_tokens": reasoning_tokens,
    }
    return {
        "answer": "".join(answer_parts).strip(),
        "reasoning_characters": len("".join(thinking_parts)), "usage": normalized_usage,
        "raw_usage": usage, "seconds": elapsed,
        "first_output_seconds": first_output, "first_answer_seconds": first_answer,
        "finish_reason": finish_reason, "served_model": served_model,
    }


def summarize(items):
    statuses = Counter(item["status"] for item in items)
    turns = [turn for item in items for turn in item.get("responses", [])]
    times = [turn["seconds"] for turn in turns]
    first_output = [turn["first_output_seconds"] for turn in turns if turn["first_output_seconds"] is not None]
    first_answer = [turn["first_answer_seconds"] for turn in turns if turn["first_answer_seconds"] is not None]
    graded = statuses["correct"] + statuses["incorrect"]
    categories = {}
    for item in items:
        category = categories.setdefault(item["category"], {"correct": 0, "incorrect": 0, "ungraded": 0, "total": 0})
        category["total"] += 1
        category[item["status"] if item["status"] in {"correct", "incorrect"} else "ungraded"] += 1
    code = [item["grading"] for item in items if item["kind"] == "code" and "grading" in item]
    content_correct = sum(bool(item.get("content_grading", item.get("grading", {})).get("passed"))
                          for item in items if item["status"] in {"correct", "incorrect"})
    return {
        "correct": statuses["correct"], "incorrect": statuses["incorrect"],
        "token_limited": statuses["token_limited"], "api_errors": statuses["api_error"],
        "empty_answers": statuses["empty_answer"], "graded_cases": graded, "total_cases": len(items),
        "accuracy_on_graded": statuses["correct"] / graded if graded else None,
        "content_correct": content_correct,
        "content_accuracy_on_graded": content_correct / graded if graded else None,
        "json_wrapper_only_failures": content_correct - statuses["correct"],
        "completed_api_requests": len(turns), "categories": categories,
        "mean_request_seconds": statistics.mean(times) if times else None,
        "median_request_seconds": statistics.median(times) if times else None,
        "max_request_seconds": max(times) if times else None,
        "median_first_output_seconds": statistics.median(first_output) if first_output else None,
        "median_first_answer_seconds": statistics.median(first_answer) if first_answer else None,
        "total_request_seconds": sum(times),
        "usage": {key: sum(turn["usage"].get(key) or 0 for turn in turns)
                  for key in ["prompt_tokens", "completion_tokens", "reasoning_tokens", "total_tokens"]},
        "code_tests": {"passed": sum(value.get("passed_tests", 0) for value in code),
                       "total": sum(value.get("total_tests", 0) for value in code)},
    }


def grade_content(bench, case, responses, strict_grading):
    """보조 진단: JSON 코드블록 외피만 제거합니다. 본 채점과 원본 답변은 유지합니다."""
    if case["kind"] not in {"json", "json_turns"}:
        return strict_grading
    import re

    normalized = []
    for turn in responses:
        answer = turn["answer"].strip()
        match = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n```", answer, re.S | re.I)
        normalized.append({**turn, "answer": match.group(1).strip() if match else answer})
    return bench.grade(case, normalized)


def summary_text(report):
    settings = report["common_settings"]
    lines = ["K-EXAONE 2.5 vs Qwen3.8-27B 자체 비교 평가", "",
             f"공통 max_tokens={settings['max_tokens']}, temperature={settings['temperature']}, top_p={settings['top_p']}, streaming=True",
             "같은 24개 문제/정답/시스템 프롬프트. 멀티턴 포함 모델당 29회 요청. 문제별 첫 응답만 채점.",
             "추론 설정은 각 모델의 profile.extra_parameters와 아래 모델 이름에 기록.",
             "내용 보조 점수는 JSON 코드블록 외피만 제거해 산출하며 엄격한 본 채점을 대체하지 않음.",
             "토큰 한도/통신 오류/빈 응답은 오답과 분리하고 완료된 답변의 정확도를 집계.",
             "응답 시간은 해당 서버/네트워크/추론 설정을 포함한 실측값이며 순수 GPU 성능 비교가 아님."]
    for profile_id, state in report["models"].items():
        summary = state["summary"]
        lines += ["", state["profile"]["label"], json.dumps(summary, ensure_ascii=False, indent=2), "문제별:"]
        for item in state["results"]:
            lines.append(f"{item['id']:3s} {item['status']:14s} {item['seconds']:7.2f}초 {item['title']}")
            if item["status"] != "correct":
                lines.append("  정답: " + json.dumps(item["expected"], ensure_ascii=False))
                if item.get("responses"):
                    lines.append("  모델 최종 답변: " + repr(item["responses"][-1]["answer"]))
                if item.get("grading"):
                    lines.append("  채점: " + json.dumps(item["grading"], ensure_ascii=False))
                if item.get("error"):
                    lines.append("  오류: " + item["error"])
    lines += ["", "한계: 소규모 자체 문제, 각 설정 1회 표본, 모델별 최적 샘플링 튜닝/다른 공개 벤치마크/512K 문맥 검증 없음.",
              "서버/모델/추론 조건이 다르므로 각 실행 설정의 비교로 해석해야 함."]
    return "\n".join(lines) + "\n"


def review_results(main_directory, thinking_directory=None):
    """저장된 답변만 검토·통합합니다. API를 다시 호출하지 않습니다."""
    import copy

    directory = Path(main_directory)
    report = json.loads((directory / "comparison.json").read_text(encoding="utf-8"))
    plan_list = json.loads((directory / "test_plan.json").read_text(encoding="utf-8"))
    plan = {case["id"]: case for case in plan_list}
    if not report.get("finished"):
        raise RuntimeError("첫 비교 실행이 아직 완료되지 않았습니다.")
    original_models = report["models"]
    report["models"] = {"exaone": original_models["exaone"], "qwen_off": original_models["qwen"]}
    report["source_runs"] = [str(directory.resolve())]
    if thinking_directory:
        thinking_path = Path(thinking_directory)
        thinking_report = json.loads((thinking_path / "comparison.json").read_text(encoding="utf-8"))
        thinking_plan = json.loads((thinking_path / "test_plan.json").read_text(encoding="utf-8"))
        assert thinking_report.get("finished"), "thinking ON 실행이 아직 완료되지 않음"
        assert thinking_plan == plan_list, "문제/정답이 다른 실행은 통합 불가"
        assert thinking_report["common_settings"] == report["common_settings"], "공통 설정 불일치"
        assert thinking_report["system_prompt"] == report["system_prompt"], "시스템 프롬프트 불일치"
        assert thinking_report["models"]["qwen"]["profile"]["extra_parameters"]["chat_template_kwargs"]["enable_thinking"] is True
        report["models"]["qwen_on"] = copy.deepcopy(thinking_report["models"]["qwen"])
        report["source_runs"].append(str(thinking_path.resolve()))
    bench_path = ROOT / "k_exaone_25_benchmark.py"
    bench = load_module("comparison_review_grader", bench_path)
    changes = []
    for profile_id, state in report["models"].items():
        assert len(state["results"]) == len(plan), f"{profile_id} 평가 미완료"
        for item in state["results"]:
            if item["status"] not in {"correct", "incorrect"}:
                continue
            original = item["grading"]
            # 코드 기능 테스트는 기존 실행 결과를 그대로 사용합니다.
            grading = original if item["kind"] == "code" else bench.grade(plan[item["id"]], item["responses"])
            item["content_grading"] = grade_content(bench, plan[item["id"]], item["responses"], grading)
            if grading != original:
                item["original_automatic_grading"] = original
                changes.append({"profile": profile_id, "case": item["id"],
                                "before": original["passed"], "after": grading["passed"],
                                "reason": grading.get("normalization_note", "채점 검토")})
            item["grading"] = grading
            item["passed"] = grading["passed"]
            item["status"] = "correct" if grading["passed"] else "incorrect"
        state["summary"] = summarize(state["results"])
    report["reviewed_at"] = datetime.now().astimezone().isoformat()
    report["reviewed_grader_sha256"] = hashlib.sha256(bench_path.read_bytes()).hexdigest()
    report["scoring_review"] = {
        "changes": changes,
        "semantic_equivalence": 'K3의 마감일 "금요일"과 "금요일까지"는 동일한 정답으로 인정',
        "secondary_content_score": "JSON 코드블록 외피만 제거. 정답 수치나 나머지 표현은 고치지 않음.",
        "original_answers_unchanged": True,
        "no_additional_api_requests": True,
    }
    serialized = json.dumps(report, ensure_ascii=False, indent=2)
    api = load_module("comparison_key_check", EXAONE_SOURCE)
    api_key = getattr(api, "API_KEY", "")
    assert not api_key or api_key not in serialized, "평가 결과에 API 키가 포함됨"
    if "--save" in sys.argv:
        (directory / "reviewed_comparison.json").write_text(serialized, encoding="utf-8")
        (directory / "reviewed_summary.txt").write_text(summary_text(report), encoding="utf-8")
    print(json.dumps({key: value["summary"] for key, value in report["models"].items()}, ensure_ascii=False, indent=2))
    if "--save" in sys.argv:
        print("REVIEWED_RESULTS=" + str(directory / "reviewed_comparison.json"))


def main():
    sys.dont_write_bytecode = True
    api = load_module("exaone_comparison_settings", EXAONE_SOURCE)
    bench_path = ROOT / "k_exaone_25_benchmark.py"
    bench = load_module("exaone_comparison_grader", bench_path)
    cases = bench.make_cases()
    profiles = [
        {"id": "exaone", "label": f"K-EXAONE 2.5 (thinking {api.REASONING_EFFORT})",
         "url": api.API_URL, "model": api.MODEL, "api_key": api.API_KEY,
         "extra_parameters": {"reasoning_effort": api.REASONING_EFFORT,
                              "chat_template_kwargs": {"preserve_thinking": api.PRESERVE_THINKING}}},
        {"id": "qwen", "label": f"Qwen3.8-27B (thinking {'ON' if QWEN_ENABLE_THINKING else 'OFF'})",
         "url": QWEN_API_URL, "model": QWEN_MODEL,
         "extra_parameters": {"chat_template_kwargs": {"enable_thinking": QWEN_ENABLE_THINKING}}},
    ]
    if "--qwen-only" in sys.argv:
        profiles = [profile for profile in profiles if profile["id"] == "qwen"]
    directory = None
    if "--save" in sys.argv:
        stamp = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d_%H%M%S")
        directory = ROOT / "llm_comparison_results" / stamp
        directory.mkdir(parents=True, exist_ok=False)
    source_hash = hashlib.sha256(EXAONE_SOURCE.read_bytes()).hexdigest()
    report = {
        "started_at": datetime.now().astimezone().isoformat(), "finished": False,
        "system_prompt": api.SYSTEM_PROMPT,
        "common_settings": {"max_tokens": MAX_TOKENS, "temperature": TEMPERATURE,
                            "top_p": TOP_P, "top_k": TOP_K, "presence_penalty": PRESENCE_PENALTY,
                            "stream": True, "include_usage": True, "keep_history": True},
        "source_sha256": source_hash,
        "grader_sha256": hashlib.sha256(bench_path.read_bytes()).hexdigest(),
        "method": "24 fixed tasks, first response only, independent sequential requests per server; two servers measured concurrently",
        "secondary_grading_rule": "JSON/code-fence wrappers removed only for secondary content grading; strict scores unchanged",
        "models": {profile["id"]: {"profile": {key: value for key, value in profile.items() if key != "api_key"},
                                    "results": [], "summary": summarize([])} for profile in profiles},
    }
    if directory is not None:
        (directory / "test_plan.json").write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
    lock = threading.Lock()

    def save():
        if directory is not None:
            (directory / "comparison.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
            (directory / "summary.txt").write_text(summary_text(report), encoding="utf-8")

    def log(message):
        with lock:
            print(message, flush=True)

    def evaluate(profile):
        state = report["models"][profile["id"]]
        with requests.Session() as session:
            warmup = request_stream(session, profile, [{"role": "user", "content": "READY라는 단어만 출력하세요."}])
            with lock:
                state["warmup_excluded"] = warmup
                save()
            log(f"[{profile['id']}] WARMUP OK {warmup['seconds']:.2f}s")
            for index, case in enumerate(cases, 1):
                log(f"[{profile['id']} {index:02d}/{len(cases)}] START {case['id']} {case['title']}")
                started = time.perf_counter()
                item = {key: case[key] for key in ["id", "category", "title", "kind", "expected"]}
                item["responses"] = []
                messages = [{"role": "system", "content": api.SYSTEM_PROMPT}] if api.SYSTEM_PROMPT else []
                try:
                    for turn_number, prompt in enumerate(case["turns"], 1):
                        messages.append({"role": "user", "content": prompt})
                        result = request_stream(session, profile, messages)
                        item["responses"].append({"turn": turn_number, "prompt": prompt, **result})
                        messages.append({"role": "assistant", "content": result["answer"]})
                        if result["finish_reason"] == "length" or not result["answer"]:
                            break
                    if any(turn["finish_reason"] == "length" for turn in item["responses"]):
                        item.update(status="token_limited", passed=None)
                    elif len(item["responses"]) != len(case["turns"]) or not item["responses"][-1]["answer"]:
                        item.update(status="empty_answer", passed=None)
                    else:
                        grading = bench.grade(case, item["responses"])
                        item.update(status="correct" if grading["passed"] else "incorrect", passed=grading["passed"], grading=grading)
                        item["content_grading"] = grade_content(bench, case, item["responses"], grading)
                except Exception as error:
                    detail = str(error).replace(api.API_KEY, "[API_KEY]")
                    item.update(status="api_error", passed=None, error=detail[:1500])
                item["seconds"] = time.perf_counter() - started
                with lock:
                    state["results"].append(item)
                    state["summary"] = summarize(state["results"])
                    save()
                    print(f"[{profile['id']} {index:02d}/{len(cases)}] {item['status'].upper()} {case['id']} {item['seconds']:.2f}s", flush=True)
                    if item["status"] != "correct":
                        print(json.dumps(item.get("grading", {"error": item.get("error")}), ensure_ascii=False), flush=True)
        return profile["id"]

    save()
    if directory is not None:
        print("RESULTS_DIR=" + str(directory), flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(evaluate, profile): profile["id"] for profile in profiles}
        for future in concurrent.futures.as_completed(futures):
            profile_id = futures[future]
            try:
                future.result()
            except Exception as error:
                with lock:
                    report["models"][profile_id]["fatal_error"] = str(error).replace(api.API_KEY, "[API_KEY]")
                    save()
                log(f"[{profile_id}] FATAL ERROR: " + report["models"][profile_id]["fatal_error"])
    report["finished"] = True
    report["finished_at"] = datetime.now().astimezone().isoformat()
    report["exaone_source_unchanged_during_run"] = hashlib.sha256(EXAONE_SOURCE.read_bytes()).hexdigest() == source_hash
    save()
    print(json.dumps({key: state["summary"] for key, state in report["models"].items()}, ensure_ascii=False, indent=2), flush=True)
    if directory is not None:
        print("RESULTS_FILE=" + str(directory / "comparison.json"), flush=True)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--qwen-thinking" in sys.argv:
        QWEN_ENABLE_THINKING = True
    if "--review" in sys.argv:
        arguments = sys.argv[sys.argv.index("--review") + 1:]
        review_results(arguments[0], arguments[1] if len(arguments) > 1 else None)
    else:
        main()
