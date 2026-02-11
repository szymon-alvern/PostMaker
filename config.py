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
            "build": ["prompt", "company_description", ("join", "topic_list", ", ")]
    }}