from pydantic import BaseModel
from dotenv import load_dotenv
from config import AI_PROVIDER_LIST
import os
from ai_provider import get_ai_provider
from typing import Any

load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class Media(BaseModel):
    company: str
    media: str


class PostRequest(Media):
    topic: str


class RepostRequest(PostRequest):
    post_description: str
    post_comment: str


class TopicRequest(Media):
    topic_list: list[str]


class PostResponse(BaseModel):
    result: Any
    tokens: int
    model: str
    error: list[str]


class EventsData(BaseModel):
    events_list: list[dict]
    media: str
    current_post: str
    conversation_context: str | None=None


def load_prompt(task: str, media: str) -> str:
    prompt_name = f"{task}_{media}.txt"
    if not os.path.exists(f"prompts/{prompt_name}"):
        raise ValueError(f"Prompt file not found: {prompt_name}")
    with open(f"prompts/{prompt_name}", "r", encoding="utf-8") as file:
        return file.read()


def load_company(company: str) -> str:
    company_name_description = f"{company}_description.txt"
    if not os.path.exists(f"descriptions/{company_name_description}"):
        raise ValueError(f"Company description not found: {company}")
    with open(f"descriptions/{company_name_description}", "r", encoding="utf-8") as file:
        return file.read()


async def post_description_generation(*,task: str | None=None, company: str | None=None, media: str | None=None,post_description: str | None=None, 
post_comment: str | None=None, topic: str | None=None, topic_list: list[str] | None=None, events: list[dict] | None = None, 
current_post: str | None = None, conversation_context: str | None=None) -> PostResponse:
    error = []
    try:
        prompt = load_prompt(task, media)
    except ValueError as e:
        raise ValueError(f"Error loading prompt: {e}")
    try:
        company_description = None
        if company:
            company_description = load_company(company=company)
    except ValueError as e:
        raise ValueError(f"Error loading company description: {e}")
    for provider in AI_PROVIDER_LIST:
        try:
            current_provider = provider["name"]
            current_model = provider["model"]
            provider = get_ai_provider(current_provider, current_model)
            response = await provider._call_api(prompt=prompt, task=task, company_description=company_description,
            topic=topic, topic_list=topic_list, post_description=post_description,  post_comment=post_comment, events=events, current_post=current_post, conversation_context=conversation_context)
            return PostResponse(result=response.get("result"), 
                tokens=response.get("tokens", 0), 
                model=response.get("model", "Unknown"), 
                error=error)
        except Exception as e:
            error.append(f"Error calling API for {current_provider} {current_model}: {e}")
    raise RuntimeError(f"Wszystkie modele zwróciły błąd: {error}")


def clear_events_date(events_list: list[dict])->list[dict]:
    if not events_list:
        raise ValueError(f'Brak listy')  
    dates = []
    for item in events_list:
        # date_obj = item.get("date")
        # if not date_obj:
        #     raise ValueError(f'Brak daty')  
        r_date = item.get("r_date")
        if not r_date:
            raise ValueError(f'Brak dat')
        available = item.get("available")
        if not isinstance(available, bool):
            raise ValueError(f'brak statusu daty')
        dates.append({"r_date": r_date.strip(), "available": available})
    return dates


