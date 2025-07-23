import time
from loguru import logger

class Timer:
    def __init__(self, name="Timer"):
        self.name = name
    def __enter__(self):
        self.start = time.time()
        logger.info(f"[{self.name}] Started.")
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start
        logger.info(f"[{self.name}] Finished in {elapsed:.2f} seconds.") 