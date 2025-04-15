import os

# root_dir
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# version
APP_VERSION = "app_ver1.0-dev"

# Chromeの実行ファイルのパス
CHROME_EXEC_PATH = "/Users/inoueritsu/Desktop/Google Chrome.app/Contents/MacOS/Google Chrome"

# Selenium用のChromeユーザープロファイル
DEV_PROFILE_PATH = "/Users/inoueritsu/dev/chrome-profile"
DEV_PROFILE_NAME = "Profile 1"

# 固定User-Agent（例）
FIXED_UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"