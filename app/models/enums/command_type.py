import enum


class CommandType(enum.StrEnum):
    query_position = "QUERY_POSITION"
    intention_check = "INTENTION_CHECK"
