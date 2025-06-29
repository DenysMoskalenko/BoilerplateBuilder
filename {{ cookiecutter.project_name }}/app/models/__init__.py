{%- if cookiecutter.project_type == "fastapi_db" %}
from pathlib import Path
import pkgutil


def load_all_models() -> None:
    """Load all models from this folder."""
    package_dir = Path(__file__).resolve().parent
    modules = pkgutil.walk_packages(
        path=[str(package_dir)],
        prefix='app.models.',
    )
    for module in modules:
        __import__(module.name)
{%- endif %}
