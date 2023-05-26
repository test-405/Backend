import logging
import os


def create_logger(name):
    """Create a logger for use in all cases."""
    loglevel = os.environ.get("LOGLEVEL", "INFO").upper()
    logging.basicConfig(
        level=loglevel,
        format="%(levelname)s - %(message)s",
        datefmt="[%Y/%m/%d %H:%M;%S]",
    )
    return logging.getLogger(name=name)
