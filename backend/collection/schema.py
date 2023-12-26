from enum import Enum

from pydantic import BaseModel


class CardType(str, Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = 'rare'
    MYTHICAL = 'mythical'


class Card(BaseModel):
    id: str
    # reference collection path
    collection: str
    type: CardType
    name: str
    info: str

    class Config:
        use_enum_values = True


class CollectionSize(int, Enum):
    forty_cards = 40
    sixty_cards = 60
    eighty_cards = 80


class Collection(BaseModel):
    size: CollectionSize = CollectionSize.forty_cards
    cards: list[str] = []
    is_active: bool = True

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True
