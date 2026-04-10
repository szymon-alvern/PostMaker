from pydantic import BaseModel
from dotenv import load_dotenv
from config import AI_PROVIDER_LIST
import os, datetime
from ai_provider import get_ai_provider
from typing import Any
from zoneinfo import ZoneInfo

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


class BasePostDate(BaseModel):
    media: str
    current_post: str
    conversation_context: str | None=None


class EventsDate(BasePostDate):
    events_list: list[dict]


class MeetingDate(BasePostDate):
    meeting_date_list: list[dict]


class DatesList(BaseModel):
    dates_list: list[dict]


class TimesList(BaseModel):
    times_list: list[dict]


class Faq(BasePostDate):
    company: str 


class FreeTermsList(BaseModel):
    terms_list: list[dict]    


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
meeting_date_list: list[dict] | None = None, current_post: str | None = None, conversation_context: str | None=None) -> PostResponse:
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
            topic=topic, topic_list=topic_list, post_description=post_description,  post_comment=post_comment, events=events, 
            meeting_date_list=meeting_date_list, current_post=current_post, conversation_context=conversation_context)
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
        date = item.get("date")
        if not date:
            raise ValueError(f'Brak dat')
        available = item.get("available")
        if not isinstance(available, bool):
            raise ValueError(f'brak statusu daty')
        dates.append({"date": date.strip(), "available": available})
    return dates


async def checking_dates_list(dates_list: list[dict]) -> str:
    if not dates_list:
        raise ValueError(f'Brak listy')
    for item in dates_list:
        date = item.get("date")
        if not date:
            raise ValueError(f'Brak dat')
        available = item.get("available")
        if not isinstance(available, bool):
            raise ValueError(f'brak statusu daty')
        if available:
            return (f'Dziękuję za zapytanie. W dniu {date} sala jest wolna. Czy możemy umówić się na krótkie spotkanie w celu omówienia szczegółów?')
    return (f'Dziękuję za zapytanie. Niestety w tych dniach sala jest niedostępna. Czy w grę wchodzą inne terminy?')


def checking_times_list(times_list: list[dict]) -> str:
    if not times_list:
        raise ValueError(f'Brak listy')
    for item in times_list:
        print("Inside for")
        start = item.get("start")
        if not start:
            raise ValueError(f'Brak czasu')
        time_utc = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ")
        date = time_utc.strftime("%d.%m.%Y")
        hour = time_utc.strftime("%H:%M")
        available = item.get("available")
        print("Checked availability")
        print(available)
        if not isinstance(available, bool):
            raise ValueError(f'brak statusu czasu')
        if available:
            return (f'Możemy spotkać się w dniu {date} o godzinie {hour}. Proszę o przesłanie numeru telefonu w celu potwierdzenia terminu.')
        else:
            return ("BOOKED")
    return ("")


def extract_free_times(terms_list: list[dict]) -> str:
    if not terms_list:
        return ("Dziś dostępne są terminy przez cały dzień.")
    item = terms_list[0]
    start = item.get("start")
    start_date_time = start.get("dateTime")
    start_date_obj = datetime.datetime.fromisoformat(start_date_time)
    warsaw_zone_obj = ZoneInfo("Europe/Warsaw")
    slot_start = start_date_obj.replace(hour=9, minute=0,second=0, microsecond=0)
    end_meeting_day = start_date_obj.replace(hour=19, minute=0, second=0, microsecond=0)
    free_times_list = []
    while slot_start <= end_meeting_day:
        slot_end = slot_start + datetime.timedelta(hours=1)
        flag = True  
        for item in terms_list:
            start_item = item.get("start")
            start_event_str = start_item.get("dateTime")
            start_event_obj = datetime.datetime.fromisoformat(start_event_str)

            event_start = start_event_obj.astimezone(warsaw_zone_obj)
            end_item = item.get("end")
            end_event_str = end_item.get("dateTime")
            end_event_obj = datetime.datetime.fromisoformat(end_event_str)
            event_end = end_event_obj.astimezone(warsaw_zone_obj)        
            if (event_start < slot_end and event_end > slot_start):
                flag = False
                break
        if flag == True:
            free_times_list.append(slot_start)
        slot_start = slot_start + datetime.timedelta(hours=1)
    if not free_times_list:
        return (f"Niestety w tym dniu nie mamy już wolnych terminów. Prosze o zaproponowanie innego terminu")    
    hours_list = []
    day_obj = free_times_list[0]
    day = day_obj.strftime("%d-%m-%Y")
    for date in free_times_list:
        hour = date.strftime("%H:%M")
        hours_list.append(hour)
    hours_list_str = ", ".join(hours_list)
    return (f"W dniu {day} mamy wolne następujące godziny: {hours_list_str}")




