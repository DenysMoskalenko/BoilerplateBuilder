{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
class BaseServiceError(Exception):
    pass


class NotFoundError(BaseServiceError):
    pass


class AlreadyExistError(BaseServiceError):
    pass
{%- endif %}
