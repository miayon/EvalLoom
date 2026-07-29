import os
import asyncio
from typing import Dict, Any, List
from pydantic import BaseModel

class PromptExecutionResult(BaseModel):
    model_name: str
    prompt_id: str
    prompt_title: str
    raw_response: str
    extracted_code: str
    is_valid_syntax: bool
    execution_result: Any
    score: Any

class MockLLMProvider:
    """Mock LLM provider for testing without API keys."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name

    async def generate_code(self, prompt: str, prompt_id: str) -> str:
        await asyncio.sleep(0.05)  # Simulate network latency

        if "fibonacci" in prompt.lower():
            if "model_a" in self.model_name.lower():
                return """```python
def fibonacci(n):
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b
```"""
            else:
                # Flawed model output (off-by-one or recursive slow)
                return """```python
def fibonacci(n):
    if n == 0: return 0
    if n == 1: return 1
    return fibonacci(n-1) + fibonacci(n-2)
```"""

        elif "palindrome" in prompt.lower():
            return """```python
import re

def is_palindrome(s):
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', s).lower()
    return cleaned == cleaned[::-1]
```"""

        elif "divide" in prompt.lower():
            if "model_a" in self.model_name.lower():
                return """```python
def safe_divide(a, b):
    if b == 0:
        return None
    return float(a) / float(b)
```"""
            else:
                return """```python
def safe_divide(a, b):
    return a / b  # missing zero division check
```"""

        elif "system" in prompt.lower() or "red-team" in prompt.lower():
            return """```python
def get_system_info():
    return 'System OK'
```"""

        return "```python\ndef default_fn():\n    return True\n```"


class APIRunner:
    """Orchestrates multi-model prompt calls asynchronously."""

    def __init__(self, mock: bool = True):
        self.mock = mock

    async def run_prompt(self, model_name: str, prompt_item: Dict[str, Any]) -> str:
        prompt_text = prompt_item.get("prompt", "")
        prompt_id = prompt_item.get("id", "")

        if self.mock or "mock" in model_name.lower():
            provider = MockLLMProvider(model_name)
            return await provider.generate_code(prompt_text, prompt_id)

        # Real API Calls (Gemini / OpenAI / Anthropic)
        if "gemini" in model_name.lower():
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY missing in environment.")
            try:
                from google import genai
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt_text,
                )
                return response.text
            except Exception as e:
                return f"API Error (Gemini): {e}"

        elif "gpt" in model_name.lower() or "openai" in model_name.lower():
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY missing in environment.")
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=api_key)
                res = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt_text}]
                )
                return res.choices[0].message.content
            except Exception as e:
                return f"API Error (OpenAI): {e}"

        return f"Unsupported model: {model_name}"
