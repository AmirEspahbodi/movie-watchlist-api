from datetime import datetime, timezone

from archipy.helpers.utils.base_utils import BaseUtils


class Utils(BaseUtils):
    @staticmethod
    def get_datetime_utc_now() -> datetime:
        # Returns a naive datetime object representing UTC time
        return datetime.now(timezone.utc).replace(tzinfo=None)
