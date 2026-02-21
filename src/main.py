import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .telegram.bot import start_bot
from .database.database import init_db
from .google_sheets.gs_export import export_to_google_sheets


async def scheduled_export_to_google_sheets():
    try:
        await export_to_google_sheets()
    except Exception as e:
        print(f"Ошибка при запланированном экспорте в Google Таблицу: {e}")


async def main():
    await init_db()
    
    scheduler = AsyncIOScheduler()
    for hour in [0, 6, 12, 18]:
        scheduler.add_job(
            scheduled_export_to_google_sheets,
            CronTrigger(hour=hour, minute=0),
        )
    await start_bot()


if __name__ == "__main__":
    asyncio.run(main())
