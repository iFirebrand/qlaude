import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = "claude-haiku-4-5-20251001"

def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

system_prompt = """ You are a patient math tutor. Do not directly answer students questions. Guide them to solutions step by step. """

def chat(messages,system=None, temperature=1.0, stop_sequences=[]):
    params = {
        "model": model,
        "max_tokens": 1024,
        "messages": messages,
        "temperature": temperature,
        "stop_sequences": stop_sequences
    }

    if system:
        params["system"] = system_prompt

    message = client.messages.create(**params)
    print(params)
    return message.content[0].text

def tutor():
    messages = []
    while True:
        user_input = input("> ")
        add_user_message(messages, user_input)
        answer = chat(messages, system_prompt)
        add_assistant_message(messages, answer)
        print("🧑‍🎓" + answer)

def interactive_chat():
    messages = []
    while True:
        user_input = input("🤷‍♂️ ")
        add_user_message(messages, user_input)
        answer = chat(messages, temperature=1.0)
        add_assistant_message(messages, answer)
        print("---")
        print(answer)
        print("---")

def stramer():
    messages = []
    add_user_message(messages, "Write a 1 sentence description of a fake database")
    # stream = client.messages.create(
    #     model=model,
    #     max_tokens = 1000,
    #     messages=messages,
    #     stream=True
    # )
    # for event in stream:
    #     print(event)
    with client.messages.stream(
        model=model,
        max_tokens=1000,
        messages=messages
    ) as stream:
        for text in stream.text_stream:
            # to stream token one at a time
            # print(text, end="")
            pass
    # to get the final msg vs. stream
    print(stream.get_final_message())

def with_assistant_message():
    messages=[]
    add_user_message(messages, "Is tea or coffee better at breakfast?")
    add_assistant_message(messages, "Coffee is better because")
    answer=chat(messages)
    print(answer)

def with_stop_sequence():
    messages=[]
    add_user_message(messages, "count 1 to 10")
    answer = chat(messages, stop_sequences=[", 5"])
    print(answer)

def structured_output():
    messages=[]
    add_user_message(messages, "Generate a very short event bridge rule as json")
    add_assistant_message(messages,"```json" )
    response = chat(messages, stop_sequences=["```"])
    # print(response)
    import json
    print(json.loads(response.strip()))


if __name__ == "__main__":
    # interactive_chat()
    # tutor()
    # stramer()
    # with_assistant_message()
    # with_stop_sequence()
    structured_output()
