from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .tasks import (
 emit_check_for_updates
)

scheduler = AsyncIOScheduler()

scheduler.add_job(emit_check_for_updates, 'interval', seconds=60*5)
