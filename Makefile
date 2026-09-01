.PHONY: dev web test lint build-web deploy

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

# Both halves also deploy automatically on push to main.
deploy:
	cd backend && vercel deploy --prod
	cd frontend && vercel deploy --prod
