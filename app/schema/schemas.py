from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

# 案件データ形式
class ProjectInfo(BaseModel):
    # 案件名
    title: str                      
    # チャネル
    platform: str
    # 案件URL
    url: str
    # 金額: 任意
    price: Optional[str]
    # 応募締切: 任意
    deadline: Optional[str]
    # 希望納期: 任意
    delivery: Optional[str]
    # 案件詳細
    detail: str
    # カテゴリー
    category: str

# 処理識別    
class HandleInfo(BaseModel):
    # 処理ID
    handle_id: str
    # ステータス
    status: str
    
# 案件一覧送信用ペイロード
class ProjectsPayload(BaseModel):
    projects: List[ProjectInfo]

# 空ペイロード
class EmptyPayload(BaseModel):
    pass

# 共通りクエスト
class BaseEnvelopeRequest(BaseModel):
    status: str
    message: Optional[str]
    handle_info: HandleInfo
    # 可変データをpayloadとして定義
    payload: Any
    

# 共通レスポンス
class BaseEnvelopeResponse(BaseModel):
    status: str
    message: Optional[str]
    handle_info: Optional[HandleInfo]    
 

# 初期リクエスト
class InitialRequest(BaseEnvelopeRequest):
    payload: EmptyPayload = EmptyPayload()

# 初期レスポンス
class InitialResponse(BaseEnvelopeResponse):
    pass

# コールバックリクエスト
class ChunkCallbackRequest(BaseEnvelopeRequest):
    payload: ProjectsPayload

# コールバック応答 
class CallbackResponse(BaseEnvelopeResponse):
    pass

