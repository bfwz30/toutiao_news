from datetime import datetime

from pydantic import BaseModel, Field
from typing import List

from schemas.base import NewsItemBase
 
# 检查收藏状态
class FavoriteCheckResponse(BaseModel):
    is_favorite: bool = Field(..., alias="isFavorite")

class FavoriteAddRequest(BaseModel):
    news_id : int = Field(..., alias="newsId")


class FavoriteNewsItemResponse(NewsItemBase):
    favorite_id:int = Field(..., alias="favoriteId")
    favorite_time:datetime = Field(..., alias="favoriteTime")
    class Config:
            # 允许使用原始字段名(user_info)或别名(UserInfo)进行赋值
            allow_population_by_field_name = True  
            # 允许直接从 ORM 模型对象读取数据
            orm_mode = True

# 收藏列表接口响应模型类
class FavoriteListResponse(BaseModel):
    list: List[FavoriteNewsItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")
 
    class Config:
            # 允许使用原始字段名(user_info)或别名(UserInfo)进行赋值
            allow_population_by_field_name = True  
            # 允许直接从 ORM 模型对象读取数据
            orm_mode = True