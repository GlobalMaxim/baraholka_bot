from datetime import datetime, timedelta
from operator import and_
from gino import Gino
from gino.schema import GinoSchemaVisitor
from bot.config import MYSQL_URI
from sqlalchemy import (Column, Integer, BigInteger, String,
                        Sequence, TIMESTAMP, JSON, TEXT, BOOLEAN)
from sqlalchemy import sql
from aiogram import types, Bot
import json
import logging

logger = logging.getLogger('utils')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="bot/logs/database.log")
formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

db = Gino()

class DuplicateArticleException(Exception):
    pass

async def create_db():
    # Устанавливаем связь с базой данных
    try:
        await db.set_bind(MYSQL_URI)
        db.gino: GinoSchemaVisitor
        await db.gino.create_all()
        print('Database connected successfully')
    except Exception:
        logger.exception('Create database exception')

class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    language = Column(String(2))
    full_name = Column(String(100))
    username = Column(String(50))
    mobile = Column(String(50))
    created_at = Column(TIMESTAMP)
    query: sql.Select

    def __repr__(self):
        return "<User(id='{}', fullname='{}', username='{}')>".format(
            self.id, self.full_name, self.username)

class Article(db.Model):
    __tablename__ = "articles"
    id = Column(Integer, Sequence('article_id_seq'), primary_key=True)
    user_id = Column(BigInteger)
    title = Column(TEXT)
    description = Column(TEXT)
    price = Column(TEXT)
    type = Column(TEXT)
    location = Column(TEXT)
    photo = Column(TEXT)
    mobile_number = Column(TEXT)
    username = Column(TEXT)
    is_approved = Column(BOOLEAN, default=False)
    is_reviewed = Column(BOOLEAN, default=False)
    created_at = Column(TIMESTAMP)
    reviewed_at = Column(TIMESTAMP)
    query: sql.Select

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    # def __repr__(self):
    #     return "<Article(id='{}', user_id='{}', title='{}', description='{}', price='{}', type='{}', location='{}', photo='{}', mobile_number='{}', username='{}')>".format(
    #         self.id, self.user_id, self.title, self.description, self.price, self.type, self.location, self.photo, self.mobile_number, self.username)
    
class DBCommands:
    async def get_user(self, user_id):
        try:
            user = await User.query.where(User.user_id == user_id).gino.first()
            return user
        except Exception:
            logger.exception('Get user')
    
    async def add_new_user(self):
        try:
            cur_date = datetime.now()
            user = types.User.get_current()
            old_user = await self.get_user(user.id)
            if old_user:
                return old_user
            new_user = User()
            new_user.user_id = user.id
            new_user.username = user.username
            new_user.full_name = user.full_name
            new_user.created_at = cur_date
            await new_user.create()
            return new_user
        except Exception:
            logger.exception('Add new user')
    
    async def set_language(self, language):
        try:
            user_id = types.User.get_current().id
            user = await self.get_user(user_id)
            await user.update(language=language).apply()
            return user
        except Exception:
            logger.exception('Set language')

    async def set_mobile(self, number):
        try:
            user_id = types.User.get_current().id
            user = await self.get_user(user_id)
            await user.update(mobile=number).apply()
        except Exception:
            logger.exception('Set mobile')

    async def delete_article(self, id):
        try:
            aricle = await Article.get(id)
            await aricle.delete()
        except Exception:
            logger.exception('Delete article')
    
    async def get_non_reviewed_articles(self):
        try:
            articles = await Article.query.where(Article.is_reviewed == False).gino.all()
            return articles
        except Exception:
            logger.exception('Get not reviewed articles')
    
    async def get_user_articles(self, user_id):
        try:
            articles = await Article.query.where(Article.user_id == user_id and Article.is_approved == True).order_by(Article.created_at.desc()).limit(10).gino.all()
            return articles
        except Exception:
            logger.exception('Get user articles')
    
    async def update_article(self, new_article: Article):
        try:
            article: Article = await Article.query.where(Article.id == new_article.id).gino.first()
            await article.update(is_approved = new_article.is_approved, is_reviewed = new_article.is_reviewed, reviewed_at = datetime.now()).apply()
        except Exception:
            logger.exception('Update article')
    
    async def get_statistic(self):
        try:
            total_users = await db.func.count(User.id).gino.scalar()
            active_posts = await (db.select([db.func.count()]).where(Article.is_approved == True)).gino.scalar()
            return total_users, active_posts
        except Exception:
            logger.exception('Get statistic')
    
    async def check_article_duplicate(self, article: Article):
        try:
            db_article: Article = await Article.query.where(and_(and_(and_(and_(Article.description == article.description, Article.title == article.title),Article.created_at >= (datetime.now() - timedelta(days=1))), Article.type == article.type),Article.user_id == article.user_id)).gino.first()
            if (db_article):
                raise DuplicateArticleException
        except Exception:
            logger.exception('Check duplicates')