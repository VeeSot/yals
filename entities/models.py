from typing import List
from main import db
import re

__author__ = 'veesot'
re_sequence = re.compile('([\d]+)\.')
re_channel = re.compile('(\d+$)')


class Entity(db.DynamicDocument):
    """"""
    # Symbolic representation for entity.For example - 1110111
    sequence = db.StringField(max_length=7, required=True)
    # Channel for signal.Range from 0 to 9.
    __channel = db.IntField(max_length=1, required=True, default=-1)
    # Set of frequency for possibly channels.For example - [0,0,1,2,0,0,5,0,0,1]
    __frequencies = db.ListField(db.IntField(), default=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def get_channel(self) -> int:
        """Returns channel number"""
        return self.__channel

    def get_frequencies(self) -> List[int]:
        """Returns list of freq"""
        return self.__frequencies

    def _set_channel(self, new_chanel: int):
        self.__channel = new_chanel

    def set_frequencies(self, new_frequencies: List[int]):
        self.__frequencies = new_frequencies

    def reset_frequencies(self):
        self.set_frequencies([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    def reset_channels(self):
        self._set_channel(-1)

    def update_channel(self):
        """Update channel use max value from freq"""
        max_value = max(self.__frequencies)
        channel_number = self.__frequencies.index(max_value)
        self._set_channel(channel_number)
        self.save()

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
            entity.save()

    @classmethod
    def add(cls, data_set: str):
        # Сразу складываем в строчку  приводя  к унифицированой последовательности вида 1110111
        sequence = ''.join(re.findall(re_sequence, data_set))
        channel = int(re.findall(re_channel, data_set)[0])  # Узнаем номер канала,что учитывать частотность по нему.
        # Возможно такая последовательность уже есть у нас в БД, поэтому стоит проверить
        entities = Entity.objects.filter(sequence=sequence)
        if entities:
            # Обновим эту запись
            entity = entities[0]
        else:
            # Нужна новая запись
            entity = Entity.objects.create(sequence=sequence)

        frequencies = entity.get_frequencies()
        frequencies[channel] += 1  # Увеличим счетчик "попаданий" на канал
        entity.set_frequencies(frequencies)
        entity.save()

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
