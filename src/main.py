import asyncio

from .telegram.bot import start_bot
from .database.database import init_db

if __name__ == "__main__":
    asyncio.run(init_db())
    asyncio.run(start_bot())
