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




class DeepSeekModel:
    """
    A simple wrapper around DeepSeek to fit the typical `model.generate(prompt)` interface.
    You can expand it to handle additional methods if needed.
    """
    def __init__(
        self,
        model_name: str = DEEPSEEK_V3_MODEL,
        system_prompt: str = "You are a helpful assistant. Respond succinctly.",
        prompt_type: str = "conversation"
    ):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.prompt_type = prompt_type

    def prompt(self, prompt: str, model: str = DEEPSEEK_V3_MODEL) -> str:
        """
        Send a prompt to DeepSeek and get detailed benchmarking response.
        """
        response = client.chat.completions.create(
            model=model, messages=[{"role": "user", "content": prompt}], stream=False
        )
        return response.choices[0].message.content


    def fill_in_the_middle_prompt(
        self, prompt: str, suffix: str, model: str = DEEPSEEK_V3_MODEL
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


    def json_prompt(self, prompt: str, model: str = DEEPSEEK_V3_MODEL, system_prompt: str ="") -> dict:
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
        self, prompt: str, prefix: str, model: str = DEEPSEEK_V3_MODEL, no_prefix: bool = False
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
        self, prompt: str, prefix: str, suffix: str, model: str = DEEPSEEK_V3_MODEL
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
        self, 
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

    def generate(self, text: str, 
                 prompt_type:str = "conversation",
                 prefix: str = "",
                 suffix: str = "",
                 no_prefix: bool = False
                 ) -> str:
        """
        This is the main entry point that the agent will call.
        For a simple usage, we treat `text` as a single user message
        and call the conversational_prompt.
        
        ### Valid prompt types:
        - conversation
        - json
        - prefix_stop
        - prefix
        - fill_in
        - prompt
        """
        if prompt_type == "conversation":
            messages = [{"role": "user", "content": text}]
            return self.conversational_prompt(
                messages=messages,
                system_prompt=self.system_prompt,
                model=self.model_name,
            )
        elif prompt_type == "json":
            return self.json_prompt(prompt=text, system_prompt=self.system_prompt)
        elif prompt_type == "prefix_stop":
            return self.prefix_then_stop_prompt(prompt=text, prefix=prefix, suffix=suffix)
        elif prompt_type == "prefix":
            return self.prefix_prompt(prompt=text, prefix=prefix, no_prefix=no_prefix)
        elif prompt_type == "fill_in":
            return self.fill_in_the_middle_prompt(prompt=text, suffix=suffix)
        elif prompt_type == "prompt":
            return self.prompt(prompt=text)