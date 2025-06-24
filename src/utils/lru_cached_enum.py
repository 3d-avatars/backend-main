from enum import Enum
from functools import lru_cache
from typing import List


class LruCachedEnum(Enum):

    @classmethod
    @lru_cache(maxsize=1)
    def values(cls) -> List:
        return [e.value for e in cls]
