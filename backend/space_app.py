"""Entry point for the Hugging Face Space.

Spaces route public traffic to port 7860, and the free tier no longer includes
the Docker SDK, so the Space is created with the Gradio SDK and simply runs this
file. It serves the same FastAPI application as everywhere else — there is no
Space-specific behaviour beyond the port.

Named space_app.py rather than app.py because `app` is already the package.
"""

import uvicorn

from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)
