import os
import uvicorn
from dotenv import load_dotenv

def main():
    """
    Load environment variables and run the FastAPI application.
    """
    # Load .env file from the project root
    load_dotenv()

    # Get host and port from environment variables, with defaults
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))

    # It's recommended to run uvicorn from the command line,
    # but this script provides a convenient way to start the server.
    # Note: `reload=True` is great for development. For production, use a process manager like Gunicorn.
    uvicorn.run(
        "assistant.main:app",
        host=host,
        port=port,
        reload=True,
        # The `reload_dirs` should point to the source code directory
        reload_dirs=["src"]
    )

if __name__ == "__main__":
    main()