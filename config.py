from zoneinfo import available_timezones


AI_PROVIDER_LIST = [
    {"name": "OpenAI", "model": "gpt-4o"},
    {"name": "Google Generative AI", "model": "gemini-2.5-flash"},
    {"name": "Anthropic", "model": "claude-3-5-sonnet-20240620"}
]

TASKS = {
    "post" : {"required": ["prompt", "company_description", "topic"],
            "build": ["prompt", "company_description", "topic"]},
    "repost": {"required": ["prompt","company_description", "topic", "post_description", "post_comment"],
            "build": ["prompt", "company_description", "topic", "post_description", "post_comment"]},
    "topic" : {"required": ["prompt", "company_description", "topic_list"],
            "build": ["prompt", "company_description", ("join", "topic_list", ", ")]},
    "availability_events" : {"required": ["prompt", "current_post", "events", "conversation_context"],
            "build": ["prompt", "current_post", ("format_events", "events", "\n"), "conversation_context"]},
    "availability_meeting" : {"required": ["prompt", "current_post", "meeting_date_list", "conversation_context"],
            "build": ["prompt", "current_post", ("format_meeting_date_list", "meeting_date_list", "\n"), "conversation_context"]}
}