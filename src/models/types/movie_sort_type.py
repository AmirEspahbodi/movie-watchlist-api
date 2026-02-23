from enum import Enum


class MovieSortColumnType(str, Enum):
    TITLE = "title"
    CREATED_AT = "created_at"
