import re
from enum import Enum
from typing import Optional

from pydantic import BaseModel, model_validator, field_validator

from firebase_db import collection_model


class CardType(str, Enum):
    """
    Enumeration of possible types of cards
    """
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = 'rare'
    MYTHICAL = 'mythical'


class Card(BaseModel):
    """Generic card schema"""
    id: Optional[str] = None
    # reference collection path
    collection: str
    type: CardType
    name: str
    info: str

    @field_validator('collection')
    @classmethod
    def check_num_card_in_collection(cls, v: str):
        """
        Check that collection size will not be exceeded after adding the card to the collection
        """
        collection_doc = collection_model.document(v).get()
        collection_dict = collection_doc.to_dict()
        nums_cards = len(collection_dict['cards'])
        if nums_cards + 1 > collection_dict['size']:
            raise ValueError(
                f'Collection has size of {collection_dict["size"]}'
            )

        return v

    @model_validator(mode='after')
    def check_card_name_in_storage(self):
        """
        Check that card name is not in storage
        """
        collection_doc = collection_model.document(self.collection).get()
        collection_cards = collection_doc.to_dict()['cards']
        cards_name_list = list(map(lambda i: re.split('[/.]', i)[1], collection_cards))
        card_name = f'{self.collection}_{self.name}_{self.type}'
        if card_name in cards_name_list:
            raise ValueError('Duplicate card')
        return self

    class Config:
        use_enum_values = True


class CollectionSize(int, Enum):
    """
    Enumeration of possible sizes of the collection
    """
    forty_cards = 40
    sixty_cards = 60
    eighty_cards = 80


class Collection(BaseModel):
    """ Generic collection schema """
    size: CollectionSize = CollectionSize.forty_cards
    cards: list[str] = []
    is_active: bool = True

    class Config:
        use_enum_values = True
        arbitrary_types_allowed = True


class UpdateSizeCollection(BaseModel):
    """ Update collection schema """
    size: CollectionSize

    class Config:
        use_enum_values = True
