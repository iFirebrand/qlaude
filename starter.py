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

def chat(messages):
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=messages,
    )
    # return message.content[0].text
    return message.content[0].text

if __name__ == "__main__":
    messages = []
    # add initial question
    add_user_message(messages, "Define bread making in one sentence")
    # pass list of messages to chat
    answer = chat(messages)
    print(answer)
    # take answer and add it as an assistant message to our list
    add_assistant_message(messages, answer)

    # follow-up question using the conversation history
    add_user_message(messages, "Now summarize that in 3 words")
    answer = chat(messages)
    print(answer)
    print(messages)

