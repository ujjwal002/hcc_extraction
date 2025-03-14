import logging
from logging.handlers import RotatingFileHandler

def configure_logging():
    """Configure detailed logging with state tracking"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - STATE_TRACKER:%(message)s',
        handlers=[
            logging.FileHandler('hcc_pipeline.log'),
            logging.StreamHandler()
        ]
    )
    logging.getLogger("langgraph").setLevel(logging.INFO)