import google.generativeai as genai
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from dotenv import load_dotenv
import os


load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")


class AIProvider:
    def __init__(self, name: str, model: str):
        self.name = name
        self.model = model


class OpenAIProvider(AIProvider):
    def __init__(self, model: str):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.model = model


    async def _call_api(self, prompt: str, company_description: str) -> str:
        content = []
        content.append({"type": "text", "text": prompt})
        content.append({"type": "text", "text": company_description})
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": content}],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content


class GoogleGenerativeAIProvider(AIProvider):
    def __init__(self, model: str):
        self.client = genai.configure(api_key=GOOGLE_API_KEY)
        self.engine = genai.GenerativeModel(model)
        self.model = model


    async def _call_api(self, prompt: str, company_description: str) -> str:
        content = [prompt, company_description]
        response = await self.engine.generate_content_async(
            contents=content,
            generation_config={"response_mime_type": "application/json"}
        )
        return response.text


class AnthropicProvider(AIProvider):
    def __init__(self, model: str):
        self.client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)
        self.model = model


    async def _call_api(self, prompt: str, company_description: str) -> str:
        content = []
        content.append({"type": "text", "text": prompt})
        content.append({"type": "text", "text": company_description})
        response = await self.client.messages.create(
            model=self.model,
            messages=[{"role": "user", "content": content}]
        )
        return response.content[0].text


def get_ai_provider(name: str, model: str) -> AIProvider:
    if name == "OpenAI":
        return OpenAIProvider(model)
    elif name == "Google Generative AI":
        return GoogleGenerativeAIProvider(model)
    elif name == "Anthropic":
        return AnthropicProvider(model)
    else:
        raise ValueError(f"Invalid provider: {name}")