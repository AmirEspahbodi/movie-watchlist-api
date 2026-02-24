from enum import Enum


class WatchStatusType(str, Enum):
    WANT_TO_WATCH = "want_to_watch"
    WATCHED = "watched"
