.PHONY: dev web test lint build-web

dev:
	cd backend && uvicorn app.main:app --reload

web:
	cd frontend && npm run dev

build-web:
	cd frontend && npm run build

test:
	cd backend && pytest

lint:
	cd backend && ruff check .
