import os
import subprocess
import time
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from ...config import DEV_PROFILE_PATH, DEV_PROFILE_NAME, CHROME_EXEC_PATH, FIXED_UA
import subprocess
import time
import re
from typing import Optional, Dict
import requests

def kill_existing_chrome(profile_path: str):
    """
    プロファイルパスに紐づくChromeプロセスを強制終了する
    """
    try:
        result = subprocess.run(
            ["pgrep", "-fl", "Chrome"],
            stdout=subprocess.PIPE,
            text=True
        )
        for line in result.stdout.splitlines():
            if profile_path in line:
                pid = int(line.split()[0])
                print(f"Killing Chrome process with PID: {pid}")
                os.kill(pid, 9)
                time.sleep(1)
    except Exception as e:
        print(f"プロセス強制終了中のエラー: {e}")


def initialize_driver(headless=False):
    """
    Selenium用 Chromeドライバの初期化処理（CDP偽装パラメータを自動取得して設定）
    """
    try:

        # 起動前に既存のプロファイル使用Chromeを kill
        kill_existing_chrome(DEV_PROFILE_PATH)
        
        # Chrome起動＆CDP情報取得（先にCDP経由で起動する）
        version_info = launch_chrome_with_cdp(
            chrome_path=CHROME_EXEC_PATH,
            user_data_dir=DEV_PROFILE_PATH,
            profile_name=DEV_PROFILE_NAME
        )
        if version_info is None:
            raise RuntimeError()

        # 起動前に既存のプロファイル使用Chromeを kill
        kill_existing_chrome(DEV_PROFILE_PATH)

        options = ChromeOptions()
        options.add_argument(f"--user-data-dir={DEV_PROFILE_PATH}")
        options.add_argument(f"--profile-directory={DEV_PROFILE_NAME}")
        options.binary_location = CHROME_EXEC_PATH

        if headless:
            options.add_argument("--headless=new")
        else:
            options.add_argument("--start-fullscreen")

        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(f"--user-agent={version_info['user_agent']}")
        options.add_argument("--ignore-certificate-errors")

        driver = Chrome(service=Service(), options=options)

        # stealth偽装
        stealth(driver,
            languages=["ja-JP", "ja"],
            vendor="Google Inc. (Apple)",
            platform="MacIntel",
            webgl_vendor="Google Inc. (Apple)",
            renderer="ANGLE (Apple, ANGLE Metal Renderer: Apple M3, Unspecified Version)",
            fix_hairline=True
        )

        # CDP偽装（sec-ch-ua / UAメタデータ）
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {
            "userAgent": version_info["user_agent"],
            "platform": "MacIntel",
            "acceptLanguage": "ja-JP,ja",
            "userAgentMetadata": {
                "brands": [
                    {"brand": "Chromium", "version": version_info["major_version"]},
                    {"brand": "Not:A-Brand", "version": "24"},
                    {"brand": "Google Chrome", "version": version_info["major_version"]}
                ],
                "fullVersion": version_info["full_version"],
                "platform": "macOS",
                "platformVersion": "10.15.7",
                "architecture": "x86",
                "model": "",
                "mobile": False
            }
        })

        return driver

    except Exception as e:
        raise RuntimeError()


def launch_chrome_with_cdp(
    chrome_path: str,
    user_data_dir: str,
    profile_name: str = "Default",  # 例: "Profile 1", "Default"
    debug_port: int = 9222
) -> Optional[Dict[str, str]]:
    """
    ChromeをCDP (remote-debugging-port) モードで指定プロファイル付きで起動し、
    バージョン情報を取得して返す。

    :return: {"user_agent": ..., "full_version": ..., "major_version": ...} or None
    """
    try:
        cmd = (
            f'"{chrome_path}" '
            f'--remote-debugging-port={debug_port} '
            f'--user-data-dir="{user_data_dir}" '
            f'--profile-directory="{profile_name}"'
        )
        subprocess.Popen(cmd, shell=True)
        time.sleep(3)  # 起動待ち

        # CDP経由でバージョン情報を取得
        res = requests.get(f"http://localhost:{debug_port}/json/version", timeout=5)
        data = res.json()

        ua = data.get("User-Agent", "")
        browser_version = data.get("Browser", "")  # 例: "Google Chrome 135.0.7049.42"
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", browser_version)
        full_version = match.group(1) if match else ""
        major_version = full_version.split('.')[0] if full_version else ""

        return {
            "user_agent": ua,
            "full_version": full_version,
            "major_version": major_version
        }

    except Exception as e:
        print(f"[CDP起動失敗] {e}")
        return None
