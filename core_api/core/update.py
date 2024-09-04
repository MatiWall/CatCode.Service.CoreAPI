import logging

from core_api.core.reader.models import CatCodeRepoEntry
from core_api.event.message_broker import produce_message

logger = logging.getLogger(__name__)
from messaging_tools import Message
from core_api.core.componentcache import cache, tracked_paths
from core_api.event.events import Events
from core_api.core.reader import repo_reader

async def check_for_updates():
    logger.debug('Checking for updated')

    files = repo_reader.files()
    for file in files:
        resp = tracked_paths.add(file)

        if resp in ('New', 'Updated'):
            logger.info(f'Component changed {file}')
            component = repo_reader.get_file_content(file)
            cache.add(component)
            event = Message(
                type=Events.COMPONENT_UPDATED,
                body=component
            )
            await produce_message(event)

    repos = set([file.name for file in files])
    cached_repos = set(tracked_paths.get_all().keys())
    deleted_repos = cached_repos - repos
    if len(list(deleted_repos)) > 0:
        try:
            tracked_paths.remove(list(deleted_repos))
            cache.remove(component)
            logger.info(f'Deleted component {list[deleted_repos]}')
        except Exception as e:
            logger.exception(f'Failed to remove deleted components with error:\n')
            return

        for deleted_file in [file for file in files if file.name in deleted_repos]:
            event = Message(
                type=Events.COMPONENT_DELETED,
                body=deleted_file
            )
            await produce_message(event)
