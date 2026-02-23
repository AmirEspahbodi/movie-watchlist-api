from enum import Enum


class RatingSortColumnType(str, Enum):
    SCORE = "score"
    CREATED_AT = "created_at"
