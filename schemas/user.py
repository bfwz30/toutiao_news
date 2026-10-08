from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

class User_Register(BaseModel):
    username : str
    password :str


class UserInfoBase(BaseModel):
    """
    用户信息基本模型
    """
    nickname :Optional[str] = Field(None,max_length=50, description= "昵称")
    avatar :Optional[str] = Field(None,max_length= 255,description="头像url")
    gender :Optional[str] =Field(None, max_length=10,description="性别")
    bio :Optional[str] = Field(None,max_length=500, description="简介")


class UserInfoResponse(UserInfoBase):
    id: int
    username :str
    # model_config = ConfigDict(
    #     from_attribute = True
    # )
    class Config:
        orm_mode = True

class UserAuthResponse(BaseModel):
    token :str
    user_info :UserInfoResponse = Field(..., alias = "UserInfo")

    # model_config = ConfigDict(
    #     populate_by_name = True,   #让UserInfo和user_info别名和字段名兼容的
    #     from_attribute = True   #允许从ORM对象中取值
    # )

    class Config:
        # 允许使用原始字段名(user_info)或别名(UserInfo)进行赋值
        allow_population_by_field_name = True  
        # 允许直接从 ORM 模型对象读取数据
        orm_mode = True

class UserUpdate(BaseModel):
    nickname:str = None
    avatar :str = None
    bio :str = None
    gender :str = None
    phone :str = None

class UserChangePassword(BaseModel):
    old_pw :str = Field(..., alias = "oldPassword",description="旧密码")
    new_pw :str =Field(..., min_length=5, alias = "newPassword",description="新密码")