import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def notify_group(group, event):
    """Send a real-time event to a channel group.

    Best effort: the database change is already saved, so a channel layer
    failure (e.g. Redis down) is logged instead of turning the request into a 500.
    """
    try:
        async_to_sync(get_channel_layer().group_send)(group, event)
    except Exception:
        logger.exception('WS notification to group %s failed', group)
