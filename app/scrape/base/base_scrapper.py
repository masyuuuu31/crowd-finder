from abc import ABC, abstractmethod
from selenium.webdriver import Chrome
from ...schema.schemas import ProjectInfo
from typing import List

class BaseScrapper(ABC):
    
    def __init__(self):
        self._seen_job_ids: set[str] = set()

    def clear_seen_jobs(self):
        self._seen_job_ids.clear()

    def is_duplicate(self, job_id: str) -> bool:
        return job_id in self._seen_job_ids

    def mark_as_seen(self, job_id: str):
        self._seen_job_ids.add(job_id)

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
