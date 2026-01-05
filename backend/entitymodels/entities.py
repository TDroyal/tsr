from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from dao.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # 存储加密后的密码
    usertype = Column(Integer, default=1)  # 用户类型
    status = Column(Integer, default=1)  # 用户状态
    email = Column(String(100), unique=True, index=True)