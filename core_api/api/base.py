from core_api.scheduler.tasks import emit_check_for_updates


async def update_repos():
    await emit_check_for_updates()
    return {'status'}