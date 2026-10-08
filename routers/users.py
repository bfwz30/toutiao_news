from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from schemas.user import User_Register, UserAuthResponse, UserInfoResponse, UserUpdate, UserChangePassword
from config.db_config import get_db
from crud import users
from starlette import status

from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(prefix="/api/user", tags = ["users"])

@router.post("/register")
async def register(user_data : User_Register, db: AsyncSession = Depends(get_db)):
    #注册逻辑： 1.先验证用户的用户名是否存在数据库，确保唯一性， 2. 唯一的话再创建用户， 
    # 3.生成token， 4. 响应结果
    uni_username = await users.get_username(db, user_data.username)
    if not uni_username:
        #raise HTTPException(status_code=404, detail= "用户名不存在， 可以创建用户")
        user = await users.register(db, user_data)
    else:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="用户名已经存在！")

    token = await users.create_token(db, user.id)
    # return {
    #     "code": 200,
    #     "message": "注册成功",
    #     "data": {
    #         "token": token,
    #         "userInfo": {
    #         "id": user.id,
    #         "username": user.username,
    #         "bio": user.bio,
    #         "avatar": user.avatar
    #         }
    #         }
    #     }
    response_data = UserAuthResponse(token = token , UserInfo = UserInfoResponse.from_orm(user))
    return success_response(message= "注册成功", data = response_data)


@router.post("/login")
async def login(user_data:User_Register, db :AsyncSession= Depends(get_db)):
    #登录逻辑 ：验证用户是否存在 -> 验证密码 -> 用户和密码都对，生成token ->返回规范的相应结果
    user = await users.login(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或者密码不对")
    token = await users.create_token(db, user.id)
    response = UserAuthResponse(token = token, UserInfo= UserInfoResponse.from_orm(user))
    return success_response(message="登录成功", data = response)
    
#查token查用户 ->封装crud -> 功能整合成一个工具函数 ->路由导入使用，依赖注入
@router.get("/info")
async def get_user_info(user:User = Depends(get_current_user)):
    # 加入这行打印代码：
    print(f"====== 当前 user 变量的内容是: {user} ======")
    print(f"====== 当前 user 的类型是: {type(user)} ======")
    return success_response(message="获取用户信息成功", data = UserInfoResponse.from_orm(user))

#修改用户信息 ：先验证token，看用户是否在登录状态 -> 更新（可选属性部分，put提交，定义请求体参数）->响应结果
@router.put("/update")
async def update_user(user_update: UserUpdate, user: User = Depends(get_current_user), db : AsyncSession= Depends(get_db)):
    update_user = await users.update_user(db, user.username,user_update)
    return success_response(message="更新用户信息成功",data = UserInfoResponse.from_orm(update_user))

@router.put("/password")
async def change_pwd(pwd_data: UserChangePassword, user :User= Depends(get_current_user), db :AsyncSession = Depends(get_db)):
    query = await users.change_pwd(db, user, pwd_data.old_pw, pwd_data.new_pw)
    if not query :
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败")
    return success_response(message="修改密码成功")