import time
import random
from typing import Union, List, Optional

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ランダムな遅延を挟む
def random_delay(delay_range=(0.2, 0.5)) -> None:
    time.sleep(random.uniform(*delay_range))


def find_element(
    driver: WebDriver,
    by: By,
    identifier: str,
    timeout: float = 0.5,
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
        print(f"要素取得失敗: {by}='{identifier}' → {e}")
        if raise_on_error:
            raise
        return [] if multiple else None
    

def find_element(
    driver: WebDriver,
    by: By,
    identifier: str,
    timeout: float = 0.5,
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
        print(f"要素取得失敗: {by}='{identifier}' → {e}")
        if raise_on_error:
            raise
        return [] if multiple else None
    

def wait_browser_load(driver: WebDriver, timeout: float = 10.0, raise_on_error: bool = False):
    """
    ブラウザのロードが完了するまでn秒待つ（初期10秒）
    """
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        return True
    except Exception as e:
        print(f"例外が発生しました: {e}")
        if raise_on_error:
            raise
        return False
        
    

def switch_or_open_tab(driver: WebDriver, url_prefix: str):
    """
    指定されたURLパターンが含まれているタブがあればそこに切り替える
    なければ新しいタブを開きアクティブ化
    """
    try:
        current_handle = driver.current_window_handle
        handles = driver.window_handles
        blank_handle = None

        # 既存のタブの中に対象URLが含まれているか確認
        for handle in handles:
            driver.switch_to.window(handle)
         
            if driver.title == "新しいタブ":
                blank_handle = handle
        
            if driver.current_url.startswith(url_prefix):
                print(f'対象のWindowHandle検出: {url_prefix} - {handle}')
                if current_handle == handle:
                    print("既にアクティブ")
                else:
                    print("タブ切り替え")
                return  # 終了
        
        if blank_handle:
            driver.switch_to.window(blank_handle)
        else:
            driver.execute_script("window.open('about:blank');")
            driver.switch_to.window(driver.window_handles[-1])  # 新しく開いたタブに切り替え
    except Exception as e:
        raise RuntimeError()
