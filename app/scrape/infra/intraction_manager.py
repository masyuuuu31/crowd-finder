from selenium.webdriver.remote.webdriver import WebDriver
import time
import random

# ランダムな遅延を挟む
def random_delay(delay_range=(0.3, 1.2)) -> None:
    time.sleep(random.uniform(*delay_range))


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
