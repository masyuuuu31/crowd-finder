import time
from ..scrape.scrapper_manager import get_scrapper
from ..scrape.infra.driver_factory import initialize_driver
from ..scrape.infra.intraction_manager import switch_or_open_tab
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
import requests


def scrape_main(handle_info: HandleInfo):
    print("スクレイピング開始")
    time.sleep(3)
    
    # ドライバー初期化
    driver = initialize_driver(headless=False)
    
    platforms = [PLATFORM_NM_CROWDWORKS, PLATFORM_NM_COCONALA, PLATFORM_NM_LANCERS]
    all_results: List[ProjectInfo] = []
    
    for platform in platforms:
        if platform:
            scrapper:BaseScrapper = get_scrapper(platform)
            results: List[ProjectInfo] = scrapper.run(driver)
            all_results.extend(results)
        
    # 50件ずつ分割して GAS側へコールバック
    gas_endpoint_url = "https://script.google.com/macros/s/AKfycbwPXJaFbv-NYoDUizvdCgf_9_YqSCMa4m_ryHLjnshaqTuM9cbE7JP16y3tjpI1-DvF/exec"
    chunk_size = 10
    total = len(all_results)
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

        except Exception as e:
            print(f"error発生: {e}")

        finally:
            print()