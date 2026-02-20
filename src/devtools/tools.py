# Запуск: python3 -m src.devtools.tools

import asyncio
from sqlalchemy import update, delete

from ..database.database import AsyncSession
from ..database.models import Student, Teacher


async def reset_all_chat_id():
    async with AsyncSession() as session:
        await session.execute(
            delete(Teacher)
        )
        await session.execute(
            update(Student)
            .values(chat_id=None)
        )
        await session.commit()
    print("Поле 'chat_id' у всех сброшено.")


async def main():
    await reset_all_chat_id()


if __name__ == "__main__":
    asyncio.run(main())
