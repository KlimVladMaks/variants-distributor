from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

"""
# Работа с сессией БД:

async with AsyncSession() as session:
    # работа с БД
    await session.commit()
"""

async_engine = create_async_engine('sqlite+aiosqlite:///database.db')
AsyncSession = async_sessionmaker(async_engine)
