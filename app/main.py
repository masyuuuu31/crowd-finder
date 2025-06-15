from .routes.scrape import router as scrape_router
from fastapi import FastAPI
from .utils.logger import setup_logger, attach_uvicorn_loggers
from .config import BASE_DIR
import os

log_file = os.path.join(BASE_DIR, "logs", "server.log")
setup_logger("app", log_file=log_file)
attach_uvicorn_loggers(log_file)

app = FastAPI()

app.include_router(scrape_router)