from fastapi import APIRouter, Body
from ..schema.schemas import InitialResponse, InitialRequest
from ..service.scrape_service import scrape_main
import threading

router = APIRouter()


@router.post("/scrape/start", response_model=InitialResponse, tags=["SCRAPE"])
async def start_scrape(
    req: InitialRequest = Body(...)
):

    # 通常処理
    threading.Thread(target=scrape_main, args=(req.handle_info,)).start()
    return InitialResponse(
        status="accepted",
        message="スクレイピングを開始しました。",
        handle_info=req.handle_info
    )