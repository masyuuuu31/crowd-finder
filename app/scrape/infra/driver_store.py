from .driver_factory import initialize_driver
from selenium.common.exceptions import WebDriverException

_driver = None

def get_shared_driver(headless=False):
    global _driver
    if _driver is None:
        _driver = initialize_driver(headless=headless)
        return _driver

    # case2: driverはあるけど、Chromeが死んでる
    try:
        if _driver.service.process is None or _driver.service.process.poll() is not None:
            print("Chromeプロセスが存在しない | 終了済み → 再起動")
            _driver.quit()
            _driver = initialize_driver(headless=headless)
    except WebDriverException as e:
        print(f"driver確認中に例外発生 → 再起動: {e}")
        _driver = initialize_driver(headless=headless)

    return _driver