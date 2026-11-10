{%- if cookiecutter.project_type in ["fastapi_agent", "fastapi_db_agent"] %}
from enum import StrEnum


class AIModelName(StrEnum):
    GPT_5_4 = 'gpt-5.4'
    GPT_5_4_MINI = 'gpt-5.4-mini'
    GPT_5_2 = 'gpt-5.2'
    GPT_5_1 = 'gpt-5.1'

    SONNET_4_6 = 'sonnet-4.6'
    OPUS_4_6 = 'opus-4.6'
    HAIKU_4_5 = 'haiku-4.5'
{%- endif %}
