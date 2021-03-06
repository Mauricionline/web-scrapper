from sqlalchemy import Column, String, Integer, Date
from datetime import date

from base import Base


class Article(Base):
    __tablename__ = 'articles'
    id = Column(String, primary_key=True)
    category = Column(String)
    body = Column(String)
    host = Column(String)
    title = Column(String)
    newspaper_uid = Column(String)
    n_tokens_body = Column(Integer)
    n_tokens_title = Column(Integer)
    url = Column(String, unique=True)
    date = Column(Date)

    def __init__(self, uid, category, body, host, newspaper_uid, n_tokens_body, n_tokens_title, title, url):
        self.id = uid
        self.category = category
        self.body = body
        self.host = host
        self.newspaper_uid = newspaper_uid
        self.n_tokens_body = n_tokens_body
        self.n_tokens_title = n_tokens_title
        self.title = title
        self.url = url
        self.date = date.today()
