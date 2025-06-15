from fastapi import APIRouter, Body
from ..schema.schemas import InitialResponse, InitialRequest, HandleInfo
from ..service.scrape_service import scrape_main
import threading
from ..utils.logger import setup_logger

from ..config import BASE_DIR
import os

log_file = os.path.join(BASE_DIR, "logs", "server.log")

# 共通ロガーをセットアップ
logger = setup_logger(__name__, log_file=log_file)

router = APIRouter()


@router.post("/scrape/start", response_model=InitialResponse, tags=["SCRAPE"])
async def start_scrape(
    req: InitialRequest = Body(...)
):
    proc_name = "start_scrape"
    logger.info(f"[{proc_name}] リクエスト受信")
    
    try:
        # 通常処理
        threading.Thread(target=scrape_main, args=(req.handle_info,)).start()
        logger.info(f"[{proc_name}] スクレイピングを非同期で開始しました")
        
        return InitialResponse(
            status="accepted",
            message="スクレイピングを開始しました。",
            handle_info=req.handle_info
        )
    
    except Exception as e:
        logger.error(f"[{proc_name}] スクレイピング起動中にエラーが発生しました。", exc_info=True)
        return InitialResponse(
            status="error",
            message="スクレイピングの起動に失敗しました。",
            handle_info=req.handle_info
        )


@router.post("/scrape/run", response_model=InitialResponse, tags=["RUN_SCRAPE"])
async def run_scrape():
    proc_name = "run_scrape"
    logger.info(f"[{proc_name}] リクエスト受信")

    handle_info = HandleInfo(
        handle_id="requestScrape",
        status="success"
    )
    
        
    try:
        # 同期的に実行
        scrape_main(handle_info)
        logger.info(f"[{proc_name}] スクレイピングを同期的に完了しました")
        
        return InitialResponse(
            status="success",
            message="スクレイピングを同期実行しました。",
            handle_info=handle_info
        )
    
    except Exception as e:
        logger.error(f"[{proc_name}] スクレイピング実行中にエラーが発生しました。", exc_info=True)
        return InitialResponse(
            status="error",
            message="スクレイピングの同期実行に失敗しました。",
            handle_info=handle_info
        )