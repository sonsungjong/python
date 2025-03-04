### Google Translate API를 사용하여 번역하는 함수를 작성
from deep_translator import GoogleTranslator

# 함수 제작
def toKorean(text):
    translator = GoogleTranslator(target='ko')
    translated_text = translator.translate(text)
    return translated_text

def toEnglish(text):
    translator = GoogleTranslator(target='en')
    translated_text = translator.translate(text)
    return translated_text

