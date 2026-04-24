import os

from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

DATABASE_URL = os.getenv("DB_URL")
DATABASE_URL_ASYNC = os.getenv("DB_ASYNC_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

async_engine = create_async_engine(DATABASE_URL_ASYNC, echo=False)
AsyncSessionLocal = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


class Todo(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean)


def init_db():
    Base.metadata.create_all(bind=engine)


async def async_init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
