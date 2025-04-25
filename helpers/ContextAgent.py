import time
import re
import json
import ollama
from typing import Optional, List, Any

class ContextAgent:
    def __init__(self, context_manager, max_retries: int = 5, delay: int = 2, default_model: str = "mistral"):
        self.context = context_manager
        self.max_retries = max_retries
        self.delay = delay
        self.default_model = default_model

    def get_string(self, key: str, system_prompt: str, user_prompt: str, model: Optional[str] = None) -> str:
        model = model or self.default_model
        self.context.initialize(key, system_prompt)
        self.context.add_user_message(key, user_prompt)

        for attempt in range(self.max_retries):
            try:
                response = ollama.chat(
                    model=model,
                    messages=self.context.get_history(key)
                )
                raw = response['message']['content'].strip()
                self.context.add_assistant_message(key, raw)
                return raw
            except (KeyError, ValueError, TypeError) as e:
                print(f"⚠️ Attempt {attempt+1} failed to get string: {e}")
                time.sleep(self.delay)

        raise RuntimeError("Failed to get a valid string response from the LLM after multiple attempts.")

    def get_int(self, key: str, system_prompt: str, user_prompt: str, model: Optional[str] = None, allowed: Optional[List[int]] = None) -> int:
        model = model or self.default_model
        self.context.initialize(key, system_prompt)
        self.context.add_user_message(key, user_prompt)

        for attempt in range(self.max_retries):
            try:
                response = ollama.chat(
                    model=model,
                    messages=self.context.get_history(key)
                )
                raw_output = response['message']['content']
                self.context.add_assistant_message(key, raw_output)

                match = re.search(r'\d+', raw_output)
                if match:
                    val = int(match.group())
                    if not allowed or val in allowed:
                        return val
                    else:
                        raise ValueError(f"Integer {val} not in allowed list: {allowed}")
                else:
                    raise ValueError("No valid number found in LLM output")
            except (KeyError, ValueError, TypeError) as e:
                print(f"❌ Attempt {attempt+1} failed to return valid int: {e}")
                time.sleep(self.delay)

        raise RuntimeError("Failed to get a valid integer response from the LLM after multiple attempts.")

    def get_json(self, key: str, system_prompt: str, user_prompt: str, model: Optional[str] = None) -> Any:
        model = model or self.default_model
        self.context.initialize(key, system_prompt)
        self.context.add_user_message(key, user_prompt)

        for attempt in range(self.max_retries):
            try:
                response = ollama.chat(
                    model=model,
                    messages=self.context.get_history(key)
                )
                raw = response['message']['content']
                self.context.add_assistant_message(key, raw)

                json_match = re.search(r'{.*}', raw, re.DOTALL)
                data = json.loads(json_match.group()) if json_match else json.loads(raw)
                return data

            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"⚠️ Attempt {attempt+1} failed to parse JSON: {e}")
                time.sleep(self.delay)

        raise RuntimeError("Failed to get valid JSON response from LLM after multiple attempts.")
