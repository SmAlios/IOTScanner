import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create file handler which logs messages
log_file_handler = logging.FileHandler("logs/logs.log")
log_file_handler.setLevel(logging.DEBUG)

# create console handler with a higher log level
log_stream_handler = logging.StreamHandler()
log_stream_handler.setLevel(logging.ERROR)

# create formatter and add it to the handlers
formatter = logging.Formatter(
    "%(asctime)s - %(filename)s - %(levelname)s - %(message)s"
)
log_file_handler.setFormatter(formatter)
log_stream_handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(log_file_handler)
logger.addHandler(log_stream_handler)
