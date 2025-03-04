from kokoro import KPipeline
from IPython.display import display, Audio
import soundfile as sf

pipeline = KPipeline(lang_code='a')

text = '''
Your best course of action is to either install the latest available stable version from PyPI or to obtain the development version directly from the source repository, after verifying that it contains the features you need. 
Always make sure to check the official documentation to confirm which version aligns with your requirements.
'''

generator = pipeline(
    text, voice='af_heart', # <= change voice here
    speed=1, split_pattern=r'\n+'
)
for i, (gs, ps, audio) in enumerate(generator):
    print(i)  # i => index
    print(gs) # gs => graphemes/text
    print(ps) # ps => phonemes
    # 오디오 파일 저장
    filename = f'my{i}.wav'
    sf.write(filename, audio, 24000)

    # 저장된 오디오 파일을 다시 불러와 재생
    display(Audio(filename, autoplay=i==0))  # 첫 번째 파일은 자동 재생