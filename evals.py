import os
from dotenv import load_dotenv
import anthropic
import json

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
model = "claude-haiku-4-5-20251001"

def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)

def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)

system_prompt = """ You are an AI assistant performing evaulations on AWS statements. """

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
    return message.content[0].text

def generate_dataset():
    prompt = """
Generate a evaluation dataset for a prompt evaluation. The dataset will be used to evaluate prompts
that generate Python, JSON, or Regex specifically for AWS-related tasks. Generate an array of JSON objects,
each representing task that requires Python, JSON, or a Regex to complete.

Example output:
```json
[
    {
        "task": "Description of task",
        "format": "json" or "python" or "regex"
    },
    ...additional
]
```

* Focus on tasks that can be solved by writing a single Python function, a single JSON object, or a regular expression.
* Focus on tasks that do not require writing much code

Please generate 3 objects.
"""

    messages = []
    add_user_message(messages, prompt)
    add_assistant_message(messages, "```json")
    text = chat(messages, stop_sequences=["```"])
    return json.loads(text)


import re
import ast


def validate_json(text):
    try:
        json.loads(text.strip())
        return 10
    except json.JSONDecodeError:
        return 0


def validate_python(text):
    try:
        ast.parse(text.strip())
        return 10
    except SyntaxError:
        return 0


def validate_regex(text):
    try:
        re.compile(text.strip())
        return 10
    except re.error:
        return 0


def grade_syntax(response, test_case):
    format = test_case["format"]
    if format == "json":
        return validate_json(response)
    elif format == "python":
        return validate_python(response)
    else:
        return validate_regex(response)


def run_prompt(test_case):
    '''Merges the prompt and test case, returns the result'''
    prompt = f"""Please solve the following task:
    
    {test_case["task"]}
    """
    messages=[]
    add_user_message(messages, prompt)
    output = chat(messages, system=system_prompt)
    return output

def grade_by_model(test_case, output):
    eval_prompt = f"""
You are an expert AWS code reviewer. Your task is to evaluate the following AI-generated solution.

Original Task:
<task>
{test_case["task"]}
</task>

Solution to Evaluate:
<solution>
{output}
</solution>

Output Format
Provide your evaluation as a structured JSON object with the following fields, in this specific order:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your overall assessment
- "score": A number between 1-10

Respond with JSON. Keep your response concise and direct.
Example response shape:
{{
    "strengths": string[],
    "weaknesses": string[],
    "reasoning": string,
    "score": number
}}
    """

    messages = []
    add_user_message(messages, eval_prompt)
    add_assistant_message(messages, "```json")
    eval_text = chat(messages, stop_sequences=["```"])
    try:
        return json.loads(eval_text)
    except json.JSONDecodeError:
        import re
        fixed = re.sub(r'\\(?!["\\\/bfnrt]|u[0-9a-fA-F]{4})', r'\\\\', eval_text)
        return json.loads(fixed)

def run_test_case(test_case):
    '''Calls run_prmpt, grades the result'''
    output = run_prompt(test_case)
    # Grading
    # score = 10
    model_grade = grade_by_model(test_case, output)
    mode_score = model_grade["score"]
    reasoning = model_grade["reasoning"]
    syntax_score = grade_syntax(output, test_case)
    score = (mode_score+syntax_score/2)

    return {
        "output": output,
        "test_case": test_case,
        "score": score,
        "reasoning": reasoning
    }

from statistics import mean
def run_eval(dataset):
    '''Loads the dataset and calls run_test_case with each caser'''
    results = []
    for test_case in dataset:
        result = run_test_case(test_case)
        results.append(result)
    
    average_score = mean([result["score"] for result in results])
    print(f"Average score: {average_score}")
    return results



if __name__ == "__main__":
    # dataset = generate_dataset()
    # with open("dataset.json", "w") as f:
    #     json.dump(dataset, f, indent=2)
    
    with open("dataset.json", "r") as f:
        dataset = json.load(f)
    results = run_eval(dataset)
    print(json.dumps(results, indent=2))