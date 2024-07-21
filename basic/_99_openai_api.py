from openai import OpenAI
client = OpenAI(api_key='key')

while True:
    user_input = input("사용자: ")
    if user_input.lower() == "0":
        print("종료합니다.")
        break

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "한국어로 존댓말로 대답해"},
            {"role": "user", "content": user_input}
        ],
        max_tokens=150,                       # 응답의 최대길이
        # temperature=0.7,                      # 응답의 창의성
        # top_p=0.9,                            # 토큰의 다양성
        # frequency_penalty=0.0,                # 반복문장 방지여부
        # presence_penalty=0.6                  # 새로운 주제 도입 가능성
    )

    print("GPT: " + completion.choices[0].message.content)