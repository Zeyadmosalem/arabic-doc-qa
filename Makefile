.PHONY: dev test lint

dev:
	cd backend && uvicorn app.main:app --reload

test:
	cd backend && pytest

lint:
	cd backend && ruff check .
