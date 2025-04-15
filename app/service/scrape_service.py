import time
import requests
from ..scrape.scrapper_manager import get_scrapper
from ..scrape.infra.driver_store import get_shared_driver
from ..scrape.infra.intraction_manager import switch_or_open_tab
from ..constants.const import PLATFORM_NM_COCONALA, PLATFORM_NM_CROWDWORKS, PLATFORM_NM_LANCERS
from ..scrape.base.base_scrapper import BaseScrapper

def scrape_main():
    print("スクレイピング開始")
    time.sleep(3)
    
    # ドライバー初期化
    driver = get_shared_driver(False)
    
    platforms = [PLATFORM_NM_LANCERS]

    for platform in platforms:
        if platform:
            scrapper:BaseScrapper = get_scrapper(platform)
            switch_or_open_tab(driver, scrapper.url_prefix)
            scrapper.run(driver)

    # 例：ダミーデータ
    data = {
        "status": "success",
        "projects": [
            {
                "title": "記事執筆依頼",
                "platform": "lancers",
                "url": "https://example.com/job/123",
                "price": "5,000円",
                "deadline": "2025-04-30",
                "delivery": "2025-05-10",
                "detail": "SEO記事の執筆をお願いします。"
            }
        ]
    }
