
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

def chat_stream_example(project_id: str, location: str) -> str:
    # [START aiplatform_gemini_multiturn_chat_stream]

    # TODO(developer): Update and un-comment below lines
    # project_id = "PROJECT_ID"
    # location = "us-central1"
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel("gemini-1.0-pro")
    chat = model.start_chat()

    def get_chat_response(chat: ChatSession, prompt: str) -> str:
        text_response = []
        responses = chat.send_message(prompt, stream=True)
        for chunk in responses:
            text_response.append(chunk.text)
        return "".join(text_response)

    prompt = "Hello."
    print(get_chat_response(chat, prompt))
    print("===========")

    prompt = "what's the country of new york"
    print(get_chat_response(chat, prompt))
    print("===========")

    prompt = "what about tyoko"
    print(get_chat_response(chat, prompt))
    print("===========")

    prompt = "what about beijing"
    print(get_chat_response(chat, prompt))
    print("===========")

    prompt = "how about paris"
    print(get_chat_response(chat, prompt))
    # [END aiplatform_gemini_multiturn_chat_stream]
    # return get_chat_response(chat, "Hello")

chat_stream_example('vertexsdk', 'us-west1')
