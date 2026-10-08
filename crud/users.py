from datetime import datetime, timedelta
import uuid

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.users import User, UserToken
from schemas.user import User_Register, UserUpdate, UserChangePassword
from utils.security import get_hash_password, verify_password
async def get_username(db: AsyncSession, username :str):
    query = select(User).where(User.username == username)
    result= await db.execute(query)
    return result.scalar_one_or_none()

async def register(db:AsyncSession, user_data : User_Register):
    #先加密密码
    hash_password = get_hash_password(user_data.password)
    user = User(username = user_data.username, password = hash_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)  #从数据库读回最新的user
    return user

async def create_token(db:AsyncSession, user_id :int):
    token = str(uuid.uuid4())
    expires_at = datetime.now()+ timedelta(days = 7)
    query  = select(UserToken).where(UserToken.id ==user_id)
    result = await db.execute(query)
    have_token = result.scalar_one_or_none()
    if have_token:
        have_token.token = token
        have_token.expires_at = expires_at
    else :
        have_token = UserToken(user_id = user_id, token = token, expires_at = expires_at)
        db.add(have_token)
        await db.commit()

    return token
        

async def login(db:AsyncSession, username:str, password :str):
    user = await get_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password,):
        return None
    return user

#根据token 查询用户 ：验证token有无，是否过期——> 没有过期，说明在登录状态，查询
async def get_user_by_token(db :AsyncSession, token:str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()
    if not db_token or db_token.expires_at < datetime.now():
        return None 
    a = select(User).where(User.id ==db_token.user_id)
    result1 = await db.execute(a)
    return result1.scalar_one_or_none()

#更新用户信息：update更新 ->检查是否命中 ->命中后，再查数据库，然后返回
async def update_user(db:AsyncSession , username :str , user_data :UserUpdate):
    query = update(User).where(User.username ==username).values(**user_data.dict(
    exclude_unset=True,
    exclude_none=True
))
    result = await db.execute(query)
    await db.commit()
    if result.rowcount ==0:
        raise HTTPException(status_code =404, detail="用户不存在")

    query = select(User).where(User.username ==username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def change_pwd(db:AsyncSession, user :User, old_pwd :str, new_pwd:str):
    if not verify_password(old_pwd,user.password):
        raise False
    new_pwd = get_hash_password(new_pwd)
    user.password =new_pwd
    #更新，由sqlalchemy真正接管这个user对象，防止session过期导致的不能提交的问题
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True