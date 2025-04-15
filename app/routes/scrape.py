from fastapi import APIRouter
from ..schema.schemas import ResponseSchema
from ..service.scrape_service import scrape_main
import threading

router = APIRouter()

@router.post("/scrape/start", response_model=ResponseSchema, tags=["SCRAPE"])
async def start_scrape():
    #　バックグラウンドでスクレイピング処理を開始
    threading.Thread(target=scrape_main).start() 
    
    return ResponseSchema(
        status="accepted",
        message="スクレイピングを開始しました。"
    )
