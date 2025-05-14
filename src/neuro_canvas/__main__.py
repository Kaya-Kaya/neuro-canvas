"""Main entry point for Neuro's Canvas application."""

import logging

from .application import start

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    start()