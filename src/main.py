import asyncio

from .telegram.bot import start_bot
from .database.database import init_db
from .google_sheets.export import export_to_google_sheets


async def background_export_to_google_sheets(interval_hours: int = 24):
    while True:
        try:
            await asyncio.sleep(interval_hours * 3600)
            await export_to_google_sheets()
        except Exception as e:
            print(f"Ошибка при фоновом экспорте в Google Таблицу: {e}")


async def main():
    await init_db()
    asyncio.create_task(background_export_to_google_sheets(interval_hours=24))
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
