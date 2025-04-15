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
    deadline: datetime = None
    # 希望納期
    delivery: datetime = None
    # 案件詳細
    detail: str


# 複数案件レスポンス
class  ProjectInfoListResponse(BaseModel):
    status: str
    projects: List[ProjectInfo]