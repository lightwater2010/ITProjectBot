from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncio
from config import PG_LINK


async_engine = create_async_engine(url=PG_LINK, echo=False)
async_session = async_sessionmaker(async_engine,
    class_=AsyncSession,
    expire_on_commit=False)

