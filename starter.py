import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

system_prompt = """ You are a patient math tutor. Do not directly answer students questions. Guide them to solutions step by step. """

def chat(messages,system=None, temperature=1.0):
    params = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "messages": messages,
        "temperature": temperature
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




if __name__ == "__main__":
    interactive_chat()
    # tutor()
