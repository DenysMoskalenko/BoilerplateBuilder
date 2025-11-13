{%- if cookiecutter.project_type == "fastapi_db" %}
from polyfactory.factories.pydantic_factory import ModelFactory

from app.api.examples.schemas import ExampleCreate


class ExampleCreateFactory(ModelFactory):
    __model__ = ExampleCreate
    __check_model__ = False
{%- endif %}
