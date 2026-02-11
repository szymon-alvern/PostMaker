import google.generativeai as genai
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
import os
import json
import re
from config import TASKS

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class AIProvider:
    def __init__(self, name: str, model: str):
        self.name = name
        self.model = model


    def _clean_json_text(self, text: str) -> str:
        if not text:
            raise ValueError("Model nic nie zwrócił")
        text = text.replace("```json", "").replace("```", "").strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        else:
            raise ValueError(f"Błąd JSON. Model zwrócił: '{text[:100]}...'")    


    def _prompt_task(self,* , prompt: str, task: str,company_description: str, 
        post_description: str | None=None, post_comment: str | None=None, 
        topic: str | None=None, topic_list: list[str] | None=None) -> list[str]:
        prompt_from_task = []
        data = {
            "prompt": prompt,
            "company_description": company_description,
            "post_description": post_description,
            "post_comment": post_comment,
            "topic": topic,
            "topic_list": topic_list
        }

        if task in TASKS:
            spec = TASKS.get(task)
            required = spec["required"]
            for r in required:
                value = data[r]
                if value is None:
                    raise ValueError(f"Brak {r}")
            build = spec["build"]    
            for b in build:   
                if isinstance(b, str):
                    value = data[b]
                elif isinstance(b, tuple):
                    value_task_name = b[1]
                    value_list = data[value_task_name]
                    if value_list is None:
                        raise ValueError(f"Brak {value_task_name}")  
                    if isinstance(value_list, list):
                        str_value_list = []
                        for i, v in enumerate(value_list):
                            if isinstance(v, str):
                                pass
                            else:
                                raise ValueError(f"{v} o indeksie {i} jest niedopuszczalnym formatem w {value_task_name}")   
                            str_value_list.append(v)
                        value = b[2].join(str_value_list)
                    else:
                        raise ValueError(f"{value_task_name} nie jest listą")
                else:
                    raise ValueError(f"{b} nie obsługiwany typ")
                if value is None:
                    raise ValueError(f"Brak {b}")
                prompt_from_task.append(value)
        else:
            raise ValueError(f"Brak obsługi zadania: {task}")
        return prompt_from_task


class OpenAIProvider(AIProvider):
    def __init__(self, model: str):
        super().__init__(name="OpenAI", model=model)
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)


    async def _call_api(self, *, prompt: str, task: str, company_description: str, 
    post_description: str | None=None, post_comment: str | None=None,
    topic: str | None=None, topic_list: list[str] | None=None) -> dict:
        prompt_from_task = self._prompt_task(prompt=prompt, task=task, company_description=company_description, 
        post_description=post_description, post_comment=post_comment, topic=topic, topic_list=topic_list)
        prompt_from_task_string = "\n".join(prompt_from_task)
        content = [{"type": "text", "text": prompt_from_task_string}]
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"}
        )
        raw_response = response.choices[0].message.content
        tokens = response.usage.total_tokens
        try:
            clean_response = self._clean_json_text(raw_response)
            result = json.loads(clean_response)
        except ValueError:
            raise ValueError(f"Błąd JSON. Model zwrócił: '{raw_response[:100]}...'")
        return {"result": result, "tokens": tokens, "model": self.model}


class GoogleGenerativeAIProvider(AIProvider):
    def __init__(self, model: str):
        super().__init__(name="Google Generative AI", model=model)
        genai.configure(api_key=GOOGLE_API_KEY)
        self.engine = genai.GenerativeModel(model)


    async def _call_api(self, *, prompt: str, task: str, company_description: str, 
    post_description: str | None=None, post_comment: str | None=None,
    topic: str | None=None, topic_list: list[str] | None=None) -> dict:
        prompt_from_task = self._prompt_task(prompt=prompt, task=task, company_description=company_description, 
        post_description=post_description, post_comment=post_comment, topic=topic, topic_list=topic_list)
        prompt_from_task_string = "\n".join(prompt_from_task)
        content = prompt_from_task_string
        response = await self.engine.generate_content_async(
            contents=content,
            generation_config={"response_mime_type": "application/json"}
        )
        raw_response = response.text
        tokens_input = response.usage_metadata.prompt_token_count
        tokens_output = response.usage_metadata.candidates_token_count
        tokens = tokens_input + tokens_output
        try:
            clean_response = self._clean_json_text(raw_response)
            result = json.loads(clean_response)
        except ValueError:
            raise ValueError(f"Błąd JSON. Model zwrócił: '{raw_response[:100]}...'")
        return {"result": result, "tokens": tokens, "model": self.model}


class AnthropicProvider(AIProvider):
    def __init__(self, model: str):
        super().__init__(name="Anthropic", model=model)
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)


    async def _call_api(self, *, prompt: str, task: str, company_description: str, 
    post_description: str | None=None, post_comment: str | None=None,
    topic: str | None=None, topic_list: list[str] | None=None) -> dict:
        prompt_from_task = self._prompt_task(prompt=prompt, task=task, company_description=company_description, 
        post_description=post_description, post_comment=post_comment, topic=topic, topic_list=topic_list)
        prompt_from_task_string = "\n".join(prompt_from_task)
        content = prompt_from_task_string
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": content}],
        )
        raw_response = response.content[0].text
        tokens_input = response.usage.input_tokens
        tokens_output = response.usage.output_tokens
        tokens = tokens_input + tokens_output
        try:
            clean_response = self._clean_json_text(raw_response)
            result = json.loads(clean_response)
        except ValueError:
            raise ValueError(f"Błąd JSON. Model zwrócił: '{raw_response[:100]}...'")
        return {"result": result, "tokens": tokens, "model": self.model}


def get_ai_provider(name: str, model: str) -> AIProvider:
    if name == "OpenAI":
        return OpenAIProvider(model)
    elif name == "Google Generative AI":
        return GoogleGenerativeAIProvider(model)
    elif name == "Anthropic":
        return AnthropicProvider(model)
    else:
        raise ValueError(f"Invalid provider: {name}")