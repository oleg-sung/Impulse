import uuid
from enum import Enum
from typing import Optional

from google.cloud.firestore_v1 import DocumentSnapshot
from pydantic import BaseModel, model_validator, Field

from backend.firebase_db import collection_model, bucket


class CardType(str, Enum):
    """
    Enumeration of possible types of cards
    """
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = 'rare'
    LEGENDARY = 'legendary'


class Card(BaseModel):
    """Generic card schema"""

    # reference collection path
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    collection: str
    type: CardType
    name: str
    info: str

    @property
    def get_collection_doc(self) -> DocumentSnapshot:
        return collection_model.document(self.collection).get()

    @model_validator(mode='after')
    def check_num_card_in_collection(self):
        """
        Check that collection size will not be exceeded after adding the card to the collection
        """
        collection_dict = self.get_collection_doc.to_dict()
        nums_cards = len(collection_dict['cards'])
        size = collection_dict['size']
        size_dict = CollectionSize.get_size_dict()
        if nums_cards + 1 > size_dict[size]:
            raise ValueError(
                f'Collection has size of {collection_dict["size"]}'
            )

        return self

    @model_validator(mode='after')
    def check_card_name_in_storage(self):
        """
        Check that card name is not in storage
        """
        collection_cards = bucket.list_blobs(prefix=f'thumbnail/{self.collection}/')
        name_list = [card.metadata['name'] for card in collection_cards]
        duplicate_list = self.name in name_list

        if duplicate_list:
            raise ValueError('Duplicate card')
        return self

    class Config:
        use_enum_values = True


class CollectionSize(str, Enum):
    """
    Enumeration of possible sizes of the collection
    """
    forty_cards = 'fortyCards'
    sixty_cards = 'sixtyCards'
    eighty_cards = 'eightyCards'

    @staticmethod
    def get_size_dict() -> dict[str, int]:
        return {
            'fortyCards': 40,
            'sixtyCards': 60,
            'eightyCards': 80
        }


class CollectionSchema(BaseModel):
    """ Generic collection schema """
    size: CollectionSize = CollectionSize.forty_cards
    cards: list[str] = []
    is_active: bool = Field(default=True, alias='isActive')
    name: str
    owner: str = Field(alias='userCreatedID')

    class Config:
        use_enum_values = True
        populate_by_name = True


class UpdateCollection(BaseModel):
    """ Update collection schema """
    is_active: Optional[bool] = Field(default=None, alias='isActive')

    class Config:
        use_enum_values = True
        populate_by_name = True
