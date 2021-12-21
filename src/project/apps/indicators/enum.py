from enum import Enum
from typing import List


class PairEnum(Enum):
    BRLBTC = 'BRLBTC'
    BRLETH = 'BRLETH'

    @classmethod
    def get_values(cls) -> List:
        return [item.value for item in cls]
