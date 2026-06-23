import logging
import sys

def setup_logging() -> None:
    """Configures Python's root logging with standard format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,  # Overrides uvicorn/fastapi default configurations on the root logger
    )

# Expose a logger to import and use anywhere in the app
logger = logging.getLogger("tasks-api")
