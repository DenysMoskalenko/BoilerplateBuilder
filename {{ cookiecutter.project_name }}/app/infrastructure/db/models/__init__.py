{%- if cookiecutter.project_type in ["fastapi_db", "fastapi_db_agent"] %}
from pathlib import Path
import pkgutil


def load_all_models() -> None:
    """Load all models from this folder."""
    package_dir = Path(__file__).resolve().parent
    modules = pkgutil.walk_packages(
        path=[str(package_dir)],
        prefix='app.infrastructure.db.models.',
    )
    for module in modules:
        __import__(module.name)
{%- endif %}
