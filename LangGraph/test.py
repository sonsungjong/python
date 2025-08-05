from transformers import pipeline
qa = pipeline(
    task="document-question-answering",
    model="naver-clova-ix/donut-base-finetuned-docvqa",
    device=0          # GPU 번호
)

res = qa("tester1.png", question="총 수량은?")
print(res)