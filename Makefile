.PHONY: dev web test lint build-web deploy

# Override with: make deploy REGION=me-central1
REGION ?= europe-west1

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

deploy:
	cd backend && gcloud run deploy arabic-doc-qa-api --source . --region $(REGION) --allow-unauthenticated --memory 2Gi --cpu 2 --timeout 300
