"""Shared persisted-HP bounds and a narrowly scoped domain error."""

MAX_STORED_HP = 2 ** 63 - 1


class HpStorageRangeError(ValueError):
    """An HP operation would produce a value SQLite cannot store."""
