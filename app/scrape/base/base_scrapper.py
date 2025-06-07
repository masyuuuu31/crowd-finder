from abc import ABC, abstractmethod
from selenium.webdriver import Chrome
from ...schema.schemas import ProjectInfo
from typing import List

class BaseScrapper(ABC):

    @property
    @abstractmethod
    def url_prefix(self) -> str:
        """
        操作対象とするURLのプレフィックス（例：'https://www.lancers.jp/'）
        """
        pass

    @abstractmethod
    def run(self, driver:Chrome) -> List[ProjectInfo]:
        """
        案件サイト毎の共通インターフェース
        """
        pass
