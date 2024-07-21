def chat_text_example(project_id: str, location: str) -> str:
    # [START aiplatform_gemini_multiturn_chat]
    import vertexai
    from vertexai.preview.generative_models import GenerativeModel, ChatSession

    # TODO(developer): Update and un-comment below lines
    # project_id = "PROJECT_ID"
    # location = "us-central1"
    vertexai.init(project=project_id, location=location)

    model = GenerativeModel("gemini-pro")
    chat = model.start_chat()

    def get_chat_response(chat: ChatSession, prompt: str) -> str:
        response = chat.send_message(prompt)
        return response.text

    prompt = "Hello."
    print(get_chat_response(chat, prompt))

    prompt = "What are all the colors in a rainbow?"
    print(get_chat_response(chat, prompt))

    prompt = "Why does it appear when it rains?"
    print(get_chat_response(chat, prompt))
    # [END aiplatform_gemini_multiturn_chat]
    return get_chat_response(chat, "Hello")


def chat_stream_example(project_id: str, location: str) -> str:
    # [START aiplatform_gemini_multiturn_chat_stream]
    import vertexai
    from vertexai.preview.generative_models import GenerativeModel, ChatSession

    # TODO(developer): Update and un-comment below lines
    # project_id = "PROJECT_ID"
    # location = "asia-northeast3"
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-pro")
    chat = model.start_chat()

    def get_chat_response(chat: ChatSession, prompt: str) -> str:
        text_response = []
        responses = chat.send_message(prompt, stream=True)
        for chunk in responses:
            text_response.append(chunk.text)
        return "".join(text_response)

    prompt = "Hello."
    print(get_chat_response(chat, prompt))

    prompt = "What are all the colors in a rainbow?"
    print(get_chat_response(chat, prompt))

    prompt = "Why does it appear when it rains?"
    print(get_chat_response(chat, prompt))
    # [END aiplatform_gemini_multiturn_chat_stream]
    return get_chat_response(chat, "Hello")

chat_text_example("AIzaSyDeo2LS0mXerZKuXVmhNkXd2znc-hMJ9eQ", "asia-northeast3")