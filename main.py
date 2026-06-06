"""Entry point — launches the Decker FastAPI backend.

The UI is a separate Streamlit app (see app/Home.py) that talks to this API
over HTTP. Run with: `uv run python main.py` or `uv run api`.
"""

from src.api.router import main

if __name__ == "__main__":
    main()
