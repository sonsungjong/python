# 3.12는 TTS 를 지원하지 않음 -> 3.10으로 다운그레이드 필수
# Rust 컴파일러 설치 필요
'''
sudo apt-get update
sudo apt-get install libsndfile1 ffmpeg
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env
pip install torch==2.9.0 torchvision==0.24.0 torchaudio==2.9.0 --index-url https://download.pytorch.org/whl/cu130
pip install "transformers==4.36.2"
pip install TTS torchcodec
'''

import torch

# ---- PyTorch 2.6+ weights_only 기본값 변경 대응 ----
_original_torch_load = torch.load


def _patched_torch_load(f, map_location=None, pickle_module=None, **pickle_load_args):
    # TTS 내부에서 torch.load(..., weights_only=?)를 안 넘기는 경우가 있어 False로 강제
    if "weights_only" not in pickle_load_args:
        pickle_load_args["weights_only"] = False
    return _original_torch_load(f, map_location=map_location, pickle_module=pickle_module, **pickle_load_args)


torch.load = _patched_torch_load

# ---- safe_globals allowlist (경고/차단 회피) ----
from TTS.tts.configs.xtts_config import XttsConfig

try:
    torch.serialization.add_safe_globals([XttsConfig])
except Exception:
    pass

# ---- torchaudio.load -> soundfile 우회 (torchcodec 불필요) ----
def patch_torchaudio_load_via_soundfile():
    try:
        import numpy as np
        import soundfile as sf
        import torchaudio as ta

        def _sf_load(path: str):
            audio, sr = sf.read(path, dtype="float32", always_2d=False)
            if getattr(audio, "ndim", 1) > 1:
                # (T, C) 또는 (C, T) 케이스가 섞일 수 있어 평균으로 단일 채널화
                audio = np.mean(audio, axis=-1)
            audio_t = torch.from_numpy(audio).float().unsqueeze(0)  # (1, T)
            return audio_t, int(sr)

        ta.load = _sf_load  # type: ignore[attr-defined]
    except Exception as e:
        print(f">> 경고: torchaudio.load 우회 패치 실패: {e}")


patch_torchaudio_load_via_soundfile()

from TTS.api import TTS

tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
tts.to("cuda" if torch.cuda.is_available() else "cpu")

print("음성 생성 시작...")
tts.tts_to_file(
    text=" 코로나19 예방수칙입니다. 손을 자주 씻기, 마스크 착용하기, 기침할 땐 입과 코 가리기, 발열, 기침, 인후통 등 증상 의심 시에는 1339 또는 보건소와 상담하시기 바랍니다.",
    file_path="output.wav",
    speaker_wav="./speaker.wav",
    language="ko",
)
print("완료: output.wav")