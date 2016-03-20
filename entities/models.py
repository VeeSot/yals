from typing import List
from main import db

__author__ = 'veesot'


class Entity(db.DynamicDocument):
    """"""
    # Symbolic representation for entity.For example - 1110111
    sequence = db.StringField(max_length=7, required=True)
    # Channel for signal.Range from 0 to 9.
    __channel = db.IntField(max_length=1, required=True, default=-1)
    # Set of frequency for possibly channels.For example - [0,0,1,2,0,0,5,0,0]
    __frequencies = db.ListField(db.IntField(), default=[0, 0, 0, 0, 0, 0, 0, 0, 0])

    def get_channel(self) -> int:
        """Returns channel number"""
        return self.__channel

    def _set_channel(self, new_chanel: int):
        self.__channel = new_chanel

    def _set_frequencies(self, new_frequencies: List[int]):
        self.__frequencies = new_frequencies

    def reset_frequencies(self):
        self._set_frequencies([0, 0, 0, 0, 0, 0, 0, 0, 0])

    def reset_channels(self):
        self._set_channel(-1)

    def update_channel(self):
        """Update channel use max value from freq"""
        max_value = max(self.__frequencies)
        channel_number = self.__frequencies.index(max_value)
        self._set_channel(channel_number)

    @classmethod
    def update_all(cls):
        all_entities = Entity.objects.all()
        for entity in all_entities:
            entity.update_channel()

    @classmethod
    def reset(cls):
        all_entities = Entity.objects.all()
        for entity in all_entities:
            entity.reset_frequencies()
            entity.reset_channels()

    @classmethod
    def get_channel_by_key(cls, key: str) -> int:
        """Return metadata about record which has sequence equal key
        :param key:sequence of symbol.For example 1110111
        """
        entities = Entity.objects.filter(sequence=key)
        if entities:
            entity = entities[0]
            return entity.get_channel()
        else:
            return None
