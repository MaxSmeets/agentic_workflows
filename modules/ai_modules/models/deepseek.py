from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Initialize DeepSeek client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com/beta"
)

DEEPSEEK_V3_MODEL = "deepseek-chat"


def prompt(prompt: str, model: str = DEEPSEEK_V3_MODEL) -> str:
    """
    Send a prompt to DeepSeek and get detailed benchmarking response.
    """
    response = client.chat.completions.create(
        model=model, messages=[{"role": "user", "content": prompt}], stream=False
    )
    return response.choices[0].message.content


def fill_in_the_middle_prompt(
    prompt: str, suffix: str, model: str = DEEPSEEK_V3_MODEL
) -> str:
    """
    Send a fill-in-the-middle prompt to DeepSeek and get response.

    The max tokens of FIM completion is 4K.

    example:
        prompt="def fib(a):",
        suffix="    return fib(a-1) + fib(a-2)",
    """
    response = client.completions.create(model=model, prompt=prompt, suffix=suffix)
    return prompt + response.choices[0].text + suffix


def json_prompt(prompt: str, model: str = DEEPSEEK_V3_MODEL, system_prompt: str ="") -> dict:
    """
    Send a prompt to DeepSeek and get JSON response.

    Args:
        prompt: The user prompt to send
        system_prompt: Optional system prompt to set context
        model: The model to use, defaults to deepseek-chat

    Returns:
        dict: The parsed JSON response
    """
    messages = [{"role":"system", "content": system_prompt},{"role": "user", "content": prompt}]

    response = client.chat.completions.create(
        model=model, messages=messages, response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)


def prefix_prompt(
    prompt: str, prefix: str, model: str = DEEPSEEK_V3_MODEL, no_prefix: bool = False
) -> str:
    """
    Send a prompt to DeepSeek with a prefix constraint and get 'prefix + response'

    Args:
        prompt: The user prompt to send
        prefix: The required prefix for the response
        model: The model to use, defaults to deepseek-chat
        no_prefix: If True, the prefix is not added to the response
    Returns:
        str: The model's response constrained by the prefix
    """
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": prefix, "prefix": True},
    ]

    response = client.chat.completions.create(model=model, messages=messages)
    if no_prefix:
        return response.choices[0].message.content
    else:
        return prefix + response.choices[0].message.content


def prefix_then_stop_prompt(
    prompt: str, prefix: str, suffix: str, model: str = DEEPSEEK_V3_MODEL
) -> str:
    """
    Send a prompt to DeepSeek with a prefix and suffix constraint and get 'response' only that will have started with prefix and ended with suffix

    Args:
        prompt: The user prompt to send
        prefix: The required prefix for the response
        suffix: The required suffix for the response
        model: The model to use, defaults to deepseek-chat

    Returns:
        str: The model's response constrained by the prefix and suffix
    """
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": prefix, "prefix": True},
    ]
    response = client.chat.completions.create(
        model=model, messages=messages, stop=[suffix]
    )
    return response.choices[0].message.content
    # return prefix + response.choices[0].message.content


def conversational_prompt(
    messages: List[Dict[str, str]],
    system_prompt: str = "You are a helpful conversational assistant. Respond in a short, concise, friendly manner.",
    model: str = DEEPSEEK_V3_MODEL,
) -> str:
    """
    Send a conversational prompt to DeepSeek with message history.

    Args:
        messages: List of message dicts with 'role' and 'content' keys
        model: The model to use, defaults to deepseek-chat

    Returns:
        str: The model's response
    """
    try:
        messages = [
            {"role": "system", "content": system_prompt},
            *messages,
        ]
        response = client.chat.completions.create(
            model=model, messages=messages, stream=False
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error in conversational prompt: {str(e)}")

def test_all_functions():
    """Display raw outputs of all functions"""
    print("\n=== Testing All Functions ===\n")
    
    # 1. Test basic prompt
    basic_response = prompt("What is the square root of 16?")
    print(f"[Prompt Function]\nInput: 'What is the square root of 16?'\nOutput:\n{basic_response}\n{'-'*40}")
    
    # 2. Test FIM
    fim_code = fill_in_the_middle_prompt(
        prompt="def multiply(a, b):\n    ",
        suffix="\n    return a * b"
    )
    print(f"[Fill-in-Middle Function]\nInput: 'def multiply(a, b):' + 'return a * b'\nOutput:\n{fim_code}\n{'-'*40}")
    
    # 3. Test JSON prompt
    json_response = json_prompt("Generate a JSON with 2 book titles")
    print(f"[JSON Function]\nInput: 'Generate a JSON with 2 book titles'\nOutput:\n{json.dumps(json_response, indent=2)}\n{'-'*40}")
    
    # 4. Test prefix prompt
    prefix_response = prefix_prompt("Complete this sentence: Artificial intelligence", " is")
    print(f"[Prefix Function]\nInput: 'Artificial intelligence' + 'is'\nOutput:\n{prefix_response}\n{'-'*40}")
    
    # 5. Test prefix+stop
    stop_response = prefix_then_stop_prompt(
        "Complete this story: In the year 2050,",
        " robots",
        " dominated"
    )
    print(f"[Prefix+Stop Function]\nInput: 'In the year 2050,' + 'robots' + 'dominated'\nOutput:\n{stop_response}\n{'-'*40}")
    
    # 6. Test conversational
    chat_history = [
        {"role": "user", "content": "Favorite programming language?"},
        {"role": "assistant", "content": "Python"}
    ]
    conv_response = conversational_prompt(chat_history)
    print(f"[Conversational Function]\nInput: Programming language conversation\nOutput:\n{conv_response}\n{'-'*40}")

if __name__ == "__main__":
    test_all_functions()