from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_TYPES = ('fastapi_db', 'fastapi_slim', 'cli_db', 'cli_slim')
PYTHON_VERSIONS = ('3.11', '3.12', '3.13')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Generate each project type and run make lint/test inside the uv environment.',
    )
    parser.add_argument(
        '--project-types',
        nargs='+',
        choices=PROJECT_TYPES,
        default=list(PROJECT_TYPES),
        help='Subset of project types to validate (default: all types).',
    )
    parser.add_argument(
        '--python-version',
        choices=PYTHON_VERSIONS,
        default='3.12',
        help='Python version to use for generated projects.',
    )
    parser.add_argument(
        '--use-otel',
        choices=('yes', 'no'),
        default='no',
        help='Toggle use_otel_observability cookiecutter answer.',
    )
    parser.add_argument(
        '--local-otel-stack',
        choices=('yes', 'no'),
        default='no',
        help='Toggle generate_local_otel_stack answer.',
    )
    parser.add_argument(
        '--output-dir',
        default='.template-builds',
        help='Base directory to store generated projects (relative to repo root). A timestamped subdir is created.',
    )
    parser.add_argument(
        '--keep-builds',
        action='store_true',
        help='Keep generated projects instead of deleting them after validation.',
    )
    parser.add_argument(
        '--run-id',
        help='Optional identifier for the generated build directory (defaults to timestamp).',
    )
    return parser.parse_args()


def run_command(
    command: list[str],
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> None:
    location = cwd if cwd is not None else Path.cwd()
    print(f"\n$ {' '.join(command)} (cwd={location})")
    if env:
        final_env = os.environ.copy()
        final_env.update(env)
        subprocess.run(command, cwd=cwd, check=True, env=final_env)
    else:
        subprocess.run(command, cwd=cwd, check=True)


def ensure_valid_options(use_otel: str, local_stack: str) -> None:
    if local_stack == 'yes' and use_otel != 'yes':
        msg = '--local-otel-stack=yes requires --use-otel=yes (mirrors template validation).'
        raise SystemExit(msg)


def make_project_name(project_type: str, use_otel: str) -> str:
    base = ''.join(part.capitalize() for part in project_type.split('_'))
    suffix = 'OtelExample' if use_otel == 'yes' else 'Example'
    return f'{base}{suffix}'


def cookiecutter_context(
    project_name: str,
    *,
    project_type: str,
    python_version: str,
    use_otel: str,
    local_stack: str,
) -> list[str]:
    return [
        f'project_name={project_name}',
        f'project_description={project_type} smoke test project',
        'author_name=Template Smoke Test',
        'author_email=smoke@test.invalid',
        f'project_type={project_type}',
        f'python_version={python_version}',
        'use_pre_commit=no',
        'use_github_actions=no',
        'initialize_git=no',
        f'use_otel_observability={use_otel}',
        f'generate_local_otel_stack={local_stack}',
        'extract_to_current_dir=Create New',
    ]


def main() -> None:
    args = parse_args()
    ensure_valid_options(args.use_otel, args.local_otel_stack)

    repo_root = Path(__file__).resolve().parents[1]
    template_root = repo_root
    run_label = args.run_id or datetime.now().strftime('%Y%m%d-%H%M%S')
    base_output_dir = (repo_root / args.output_dir).resolve()
    output_root = (base_output_dir / run_label).resolve()
    replay_dir = output_root / '.cookiecutter_replay'
    uv_cache_dir = output_root / '.uv-cache'
    uv_cache_dir.mkdir(parents=True, exist_ok=True)

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    generated: list[Path] = []

    try:
        for project_type in args.project_types:
            project_name = make_project_name(project_type, args.use_otel)
            destination = output_root / project_name

            print(f'\n=== Generating {project_type} -> {destination} ===')
            command = [
                'cookiecutter',
                str(template_root),
                '--no-input',
                '--output-dir',
                str(output_root),
                *cookiecutter_context(
                    project_name,
                    project_type=project_type,
                    python_version=args.python_version,
                    use_otel=args.use_otel,
                    local_stack=args.local_otel_stack,
                ),
            ]
            replay_dir.mkdir(parents=True, exist_ok=True)
            run_command(
                command,
                env={
                    'COOKIECUTTER_REPLAY_DIR': str(replay_dir),
                    'HOME': str(output_root),
                    'UV_CACHE_DIR': str(uv_cache_dir),
                },
            )

            generated.append(destination)

            print(f'\n=== Syncing dependencies for {project_name} ===')
            run_command(['uv', 'sync'], cwd=destination, env={'UV_CACHE_DIR': str(uv_cache_dir)})

            print(f'\n=== Running lint for {project_name} ===')
            run_command(['uv', 'run', 'make', 'lint'], cwd=destination, env={'UV_CACHE_DIR': str(uv_cache_dir)})

            print(f'\n=== Running tests for {project_name} ===')
            run_command(['uv', 'run', 'make', 'test'], cwd=destination, env={'UV_CACHE_DIR': str(uv_cache_dir)})

        print('\n✅ Completed lint & test runs for all requested project types.')
    finally:
        if not args.keep_builds and output_root.exists():
            print(f'\n🧹 Removing generated projects in {output_root}')
            shutil.rmtree(output_root)


if __name__ == '__main__':
    main()
