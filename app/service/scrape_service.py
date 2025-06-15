import time
from ..scrape.scrapper_manager import get_scrapper
from ..scrape.infra.driver_factory import initialize_driver
from ..constants.const import (
    PLATFORM_NM_COCONALA, 
    PLATFORM_NM_CROWDWORKS, 
    PLATFORM_NM_LANCERS, 
    DEBUG_MODE
)
from ..scrape.base.base_scrapper import BaseScrapper
from typing import List
from ..schema.schemas import (
    ProjectInfo, 
    ChunkCallbackRequest, 
    HandleInfo,
    ProjectsPayload
)
from ..config import GAS_ENDPOINT
import requests
from ..utils.logger import setup_logger

# 共通ロガーをセットアップ
logger = setup_logger(__name__)


def scrape_main(handle_info: HandleInfo):
    proc_name = "scrape_main"
    logger.info(f"[{proc_name}] スクレイピング開始")
    
    time.sleep(3)
    
    try:
        # ドライバー初期化
        driver = initialize_driver(headless=True)
    except Exception as e:
        logger.error(f"[{proc_name}] ドライバー初期化に失敗しました", exc_info=True)
        return
    
    
    platforms = [PLATFORM_NM_CROWDWORKS, PLATFORM_NM_LANCERS, PLATFORM_NM_COCONALA]
    all_results: List[ProjectInfo] = []
    
    for platform in platforms:
        if platform:
            logger.info(f"[{proc_name}] プラットホーム処理開始: {platform}")
            try:
                scrapper:BaseScrapper = get_scrapper(platform)
                results: List[ProjectInfo] = scrapper.run(driver)
                all_results.extend(results)
            except Exception as e:
                logger.error(f"[{proc_name}] {platform}スクレイピング中にエラーが発生", exc_info=True)

    # 50件ずつ分割して GAS側へコールバック
    gas_endpoint_url = GAS_ENDPOINT
    chunk_size = 10
    total = len(all_results)
    logger.info(f"[{proc_name}] 合計取得件数: {total}件 / 分割単位:{chunk_size}件")
    
    for start in range(0, total, chunk_size):
        
        try:
            chunk = all_results[start: start + chunk_size]

            req_body = ChunkCallbackRequest(
                status="success",
                message="None",
                handle_info=handle_info,
                payload=ProjectsPayload(projects=chunk)
            )

            resp = requests.post(
                    gas_endpoint_url,
                    json=req_body.model_dump()
                    )
            resp.raise_for_status()
            logger.info(f"[{proc_name}] {start}~{start + len(chunk)}件目を送信完了")
        
        except Exception as e:
            logger.error(f"[{proc_name}] チャンク送信失敗: {start}~{start + len(chunk)}件目", exc_info=True)

    
    logger.info(f"[{proc_name}] スクレイピング処理終了")
    