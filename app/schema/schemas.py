from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# 共通のレスポンス形式
class ResponseSchema(BaseModel):
    status: str
    message: Optional[str] = None


# 案件データ形式
class ProjectInfo(BaseModel):
    # 案件名
    title: str                      
    # チャネル
    platform: str
    # 案件URL
    url: str
    # 金額
    price: str
    # 応募締切
    deadline: str
    # 希望納期
    delivery: str
    # 案件詳細
    detail: str
    # 取引ページURL
    trading_url: str
    # カテゴリー
    category: str


# 複数案件レスポンス
class  ProjectInfoListResponse(BaseModel):
    status: str
    projects: List[ProjectInfo]