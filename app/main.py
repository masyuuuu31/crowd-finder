from .routes.scrape import router as scrape_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(scrape_router)