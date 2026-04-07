{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.fields import Use

from app.api.v1.examples.schemas import ExampleCreate


class ExampleCreateFactory(ModelFactory[ExampleCreate]):
    __model__ = ExampleCreate
    __check_model__ = False

    name = Use(lambda: ExampleCreateFactory.__faker__.sentence(nb_words=3).rstrip('.'))
    description = Use(lambda: ExampleCreateFactory.__faker__.text(max_nb_chars=500))
    birthday = Use(lambda: ExampleCreateFactory.__faker__.date_of_birth())
{%- endif %}
