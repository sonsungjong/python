from transformers import AutoProcessor, SeamlessM4Tv2Model
import torchaudio
import scipy.io.wavfile as wav
import torch
import numpy as np
import datetime
# print("PyTorch 버전:", torch.__version__)
# print("CUDA 지원 여부:", torch.cuda.is_available())
# print("PyTorch가 인식한 CUDA 버전:", torch.version.cuda)
# print("GPU 개수:", torch.cuda.device_count())
# print("GPU 이름:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CUDA 없음")


# pip install git+https://github.com/huggingface/transformers.git sentencepiece
# python3.11.6, torch2.4.0, torchaudio2.4.0, cuda124
# 1. 모델을 cuda124 로 로드 (python3.11.6, torch2.4.0, torchaudio2.4.0, cuda124)
processor = AutoProcessor.from_pretrained("facebook/seamless-m4t-v2-large")
model = SeamlessM4Tv2Model.from_pretrained("facebook/seamless-m4t-v2-large").to("cuda")

# 2. 텍스트 입력 (영어버전eng, 한국버전kor 등)
# text_inputs = processor(text = "Hello, My Name is Sungjong Son.", src_lang="eng", return_tensors="pt")
text_inputs = processor(text = "안녕하세요, 저는 손성종 입니다.", src_lang="kor", return_tensors="pt")

# 3. 입력 데이터를 GPU로 이동
text_inputs = {key: val.to("cuda") for key, val in text_inputs.items()}

# 5. 해당 언어로 음성 변환 (TTS)
audio_array_from_text = model.generate(**text_inputs, tgt_lang="kor")[0].cpu().numpy().squeeze()
# audio_array_from_text = model.generate(**text_inputs, tgt_lang="eng")[0].cpu().numpy().squeeze()

# 6. 샘플링 속도 가져오기
sample_rate = model.config.sampling_rate

# 7. float32 -> int16 변환 (WAV 저장을 위해)
audio_int16 = np.int16(audio_array_from_text * 32767)

# 8. 현재 날짜와 시간을 지정된 형식으로 WAV 파일 저장
timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
filename = f"tts_{timestamp}.wav"
wav.write(filename, rate=sample_rate, data=audio_int16)

print(f"✅ '{filename}' 파일이 저장되었습니다.")

# 오디오 파일 읽기
# audio, orig_freq =  torchaudio.load("my_audio.wav")
# 16kHz로 변환 (모델 요구사항)
# audio =  torchaudio.functional.resample(audio, orig_freq=orig_freq, new_freq=16_000) # must be a 16 kHz waveform array
# 모델 입력 형식으로 변환 (pt)
# audio_inputs = processor(audios=audio, return_tensors="pt")
# 
# audio_array_from_audio = model.generate(**audio_inputs, tgt_lang="kor")[0].cuda().numpy().squeeze()
