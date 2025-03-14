import logging
from logging.handlers import RotatingFileHandler

def configure_logging():
    """Configure logging with rotation"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'hcc_pipeline.log',
                maxBytes=10*1024*1024,
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )