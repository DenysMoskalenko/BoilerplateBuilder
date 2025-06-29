{%- if cookiecutter.project_type == "fastapi_db" %}
class BaseServiceError(Exception):
    pass


class NotFoundError(BaseServiceError):
    pass


class AlreadyExistError(BaseServiceError):
    pass
{%- else %}
class BaseServiceError(Exception):
    pass
{%- endif %}