from fastapi import APIRouter, Depends, HTTPException,Query
from crud import news
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db

router = APIRouter(prefix="/api/news", tags = ["news"])


#-----------------接口实现流程----------------
# 1. 模块化路由  ——> 根据前端的 api接口文档
# 2.定义模型类 ——> 根据数据库表来定义
# 3.在crud里面创建文件，封装操作数据库的方法
# 4.在路由函数里面调用crud封装好的方法，返回data结果 

@router.get("/categories")
async def get_ca(skip : int = 0, limit :int =100, db : AsyncSession = Depends(get_db)):
    news_class  = await news.get_categories(db, skip, limit)
    return {
        "code" :200,
        "message" : "获取新闻分类成功",
        "data":  news_class

    }


@router.get("/list")
async def get_news_list(
    category_id : int = Query(..., alias = "categoryId"),
    page : int =1,
    page_size :int = Query(10,alias = "pageSize", le =100),
    db: AsyncSession = Depends(get_db)
):
    offset = (page -1)*page_size
    news_list = await news.get_news_list(db,category_id, offset, page_size)
    total = await news.get_news_count(db,category_id)
    has_more = (offset + len(news_list)<total)
    return {
        "code" :200,
        "message" : "获取新闻列表成功",
        "data":{
            "list": news_list,
            "total" : total,
            "hasMore" : has_more
        }
    }


@router.get("/detail")
async def get_news_detail(news_id : int = Query(..., alias = "id"), db : AsyncSession = Depends(get_db)):
    news_detail = await news.get_news_detail(db, news_id)
    if not news_detail:
        raise HTTPException(status_code = 404, detail = "新闻不存在")

    views = await news.increase_views(db, news_detail.id)
    if not views:
        raise HTTPException(status_code = 404, detail = "新闻不存在")
    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)    
    return {
        "code" :200,
        "message" : "success",
        "data": {
            "id" : news_detail.id,
            "title" :news_detail.title ,
            "content" : news_detail.content,
            "image" : news_detail.image,
            "author" : news_detail.author,
            "publishTime" : news_detail.publish_time,
            "categoryId" : news_detail.category_id,
            "views" : news_detail.views,
            "relatedNews" : related_news
        }
    }

