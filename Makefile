build:
	uv sync --dev

run:
	uv run fastapi dev app/main.py --port 8000 --host 0.0.0.0

test:
	uv run pytest -vvvv

lint:
	uv run ruff check . --select I --fix
	uv run ruff format .
