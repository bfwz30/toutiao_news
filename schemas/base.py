from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
 
 
class NewsItemBase(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    image: Optional[str] = None
    author: Optional[str] = None
    category_id: int = Field(alias="categoryId")
    views: int
    publish_time: Optional[datetime] = Field(None, alias="publishedTime")
 
    class Config:
            # 允许使用原始字段名(user_info)或别名(UserInfo)进行赋值
            allow_population_by_field_name = True  
            # 允许直接从 ORM 模型对象读取数据
            orm_mode = True