import time
import random
from typing import Union, List, Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ...utils.logger import setup_logger

logger = setup_logger(__name__)

# ランダムな遅延を挟む
def random_delay(delay_range=(0.5, 1.0)) -> None:
    """
    指定された範囲でランダムな遅延を挟む
    """
    time.sleep(random.uniform(*delay_range))


def find_element(
    driver: WebDriver,
    by: By,
    identifier: str,
    timeout: float = 3.0,
    multiple: bool = False,
    raise_on_error: bool = False
) -> Union[Optional[WebElement], List[WebElement]]:
    """
    単一または複数の要素を取得するユーティリティ関数。

    Args:
        driver (WebDriver): 対象ドライバ。
        by (By): 検索方法。
        identifier (str): セレクタ文字列。
        timeout (float): 最大待機時間。
        multiple (bool): Trueなら複数要素、Falseなら単一要素。
        raise_on_error (bool): エラー時に例外を投げるか。

    Returns:
        WebElement | List[WebElement] | None | []
    """
    proc_name = "find_element"
    
    try:
        random_delay()
        wait = WebDriverWait(driver, timeout)
        if multiple:
            elements = wait.until(EC.presence_of_all_elements_located((by, identifier)))
            return elements
        else:
            element = wait.until(EC.presence_of_element_located((by, identifier)))
            return element
    except Exception as e:
        logger.warning(f"[{proc_name}] 要素取得失敗: '{by}={identifier}' timeout={timeout}", exc_info=True)
        if raise_on_error:
            raise
        return [] if multiple else None
    


def wait_browser_load(driver: WebDriver, timeout: float = 10.0, raise_on_error: bool = False):
    """
    ブラウザのロードが完了するまでn秒待つ（初期10秒）
    """
    proc_name = "wait_browser_load"
    
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except Exception as e:
        logger.warning(f"[{proc_name}] ブラウザロード待機中に例外発生", exc_info=True)
        if raise_on_error:
            raise
        return False
