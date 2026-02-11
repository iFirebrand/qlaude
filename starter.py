import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append

def send_message(user_prompt: str) -> str:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=[
            {
                "role": "user", 
                "content": user_prompt
            }
        ],
    )
    # return message.content[0].text
    return message.content[0].text


if __name__ == "__main__":
    response = send_message("Hello, Claude! Say one sentence.")
    print(response)

