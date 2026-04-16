# Expose the FastAPI app for backwards compatibility with legacy 'app:app' commands
try:
    from main import app
except ImportError:
    # This might happen if running from a different context where main is not available
    pass
