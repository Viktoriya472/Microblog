import os
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()

DATABASE_URL = os.getenv('psql')

engine = create_async_engine(DATABASE_URL)

async_session_maker = async_sessionmaker(autocommit=False,
                                         autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass
