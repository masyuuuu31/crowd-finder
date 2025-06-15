from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ChromeOptions
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager  # 追加
from ...utils.logger import setup_logger

from ...config import BASE_DIR
import os

log_file = os.path.join(BASE_DIR, "logs", "server.log")

# 共通ロガーをセットアップ
logger = setup_logger(__name__, log_file=log_file)

def initialize_driver(headless=False):
    """
    Selenium用 Chromeドライバの初期化処理（stealth + headless 対応）
    """
    proc_name = "initialize_driver"
    
    try:
        logger.info(f"[{proc_name}] Chromeドライバ初期化開始 (headless={headless})")
        options = ChromeOptions()

        # ヘッドレスまたは全画面
        if headless:
            logger.debug(f"[{proc_name}] ヘッドレスモードで起動")
            options.add_argument("--headless=new")
        else:
            logger.debug(f"[{proc_name}] 全画面モードで起動")
            options.add_argument("--start-fullscreen")

        # Bot検知回避
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # UA固定（任意で調整可）
        options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")

        # 安定性向上用オプション
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        logger.info(f"[{proc_name}] ChromeDriverを起動中…")
        # ChromeDriver を自動取得
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        logger.debug(f"[{proc_name}] stealthオプションを適用中…")
        # stealth 偽装
        stealth(driver,
            languages=["ja-JP", "ja"],
            vendor="Google Inc. (Apple)",
            platform="MacIntel",
            webgl_vendor="Google Inc. (Apple)",
            renderer="ANGLE (Apple, ANGLE Metal Renderer: Apple M3, Unspecified Version)",
            fix_hairline=True
        )

        logger.info(f"[{proc_name}] Chromeドライバ初期化完了")
        return driver

    except Exception as e:
        logger.exception(f"[{proc_name}] Chromeドライバ初期化に失敗しました")
        raise RuntimeError(f"Driver initialization failed: {e}")
