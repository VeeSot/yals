import json
from typing import List
import Levenshtein
from collections import Counter
import flask
from flask import Blueprint, render_template
from flask.views import MethodView

entities = Blueprint('entities', __name__, template_folder='templates')


class EntityView(MethodView):
    def get(self):
        return render_template('index.html')


class EntityAdd(MethodView):
    def post(self, *args, **kwargs):
        """Обработка входящих учебных данных"""
        raw_data_sets = get_request_data()
        for data_set in raw_data_sets:
            Records.add(data_set)  # Сложим все записи в хранилище
        # После чего стоит пересчмитать данные и одновить укзатели на каналы которые мы считаем приоритетными
        Records.update_all()
        response = {'status': 'Database was updated'}
        return flask.jsonify(**response)


class EntityTest(MethodView):
    def post(self):
        """Обработка входящих тестовых данных"""
        pairs = []
        raw_data_sets = get_request_data()
        for data_set in raw_data_sets:
            sequence = Records.data_set_to_sequence(data_set)
            channel = Records.get_channel_by_key(sequence)  # Канал на который укажет набор данных
            if channel is None or channel == -1:
                channel = get_most_possible_channel(sequence)
                if channel is None:  # Так и не нашли ничего подходящего.Например загнали тестовую выборку в пустую базу
                    channel = "Канал неизвестен"
            pairs.append({'key': data_set, 'value': channel})
        response = {'status': 'Comprehension complete', 'pairs': pairs}
        return flask.jsonify(**response)


class DataBaseView(MethodView):
    def delete(self):
        Records.drop_all()
        response = {'status': 'Database was dropped'}
        return flask.jsonify(**response)


def get_request_data() -> List[str]:
    """Получаем данные из запроса,чистим и возвращаем набор данных
    """
    data = json.loads(flask.request.data.decode())
    learn_data = data.get('data')  # Всё содержание обучающего файла
    learn_data = learn_data.replace('\r\n', '\n')  # Унификация для файлов созданых в Win
    data_sets = learn_data.split('\n')
    pointer = 0  # Указатель на позицию чтения data_sets
    # Идем по набору данных пока не встретим информацию о количестве входных значений
    for data_set in data_sets:
        pointer += 1
        if -1 != data_set.find('@data'):
            # Следующей строчкой пойдут  данные.Пора прерваться
            break
    raw_data_sets = data_sets[pointer:]
    raw_data_sets = filter(lambda x: x != '', raw_data_sets)  # Игнорируем пустые строки
    return raw_data_sets


def get_most_possible_channel(sequence: str) -> int:
    records = Records.objects.all()
    records_metadata = {record.sequence: record.get_channel() for record in records}
    list_of_sequence = list(records_metadata.keys())  # Все последовательности о которых мы знаем что либо
    # Отправим искать соседей
    neighbors = []
    # Количество изменений в поледовательности необходимое для того чтоб найти подобных.
    # Будем пошагово увеличивать до максимально возможного растояния
    distance = 1
    try:
        max_distance = len(list_of_sequence[0])  # У нас всегда есть как минимум одна запись в БД
    except IndexError:  # Ну или почти всегда.Если нет даже этого, то и смысла искать - нет.
        return None
    while not neighbors and distance <= max_distance:
        neighbors = find_neighbors(sequence, list_of_sequence, distance)
        distance += 1  # Постепенно мы увеличиваем "расстояние" по которому записи будут считаться похожими
    # После чего  стоит проверить нашли ли мы вообще каких то соседей.А если нашли - на какой канал они нам покажут
    if neighbors:
        current_channel = -1  # Изначально мы не знаем какой канал приоритетнее
        current_freq = 0
        channels_of_neighbors = [Records.get_channel_by_key(neighbor) for neighbor in neighbors]
        freq_of_channel = Counter(channels_of_neighbors)  # Частота встречаемости каналов
        channels = freq_of_channel.keys()
        for channel in channels:
            freq = freq_of_channel.get(channel)  # Количество "соседей" на этом канале
            if freq > current_freq:
                current_freq = freq
                current_channel = channel
        return current_channel
    else:
        return None


def find_neighbors(sequence: str, list_of_sequence: List[str], distance: int) -> list:
    neighbors = []
    for test_sequence in list_of_sequence:
        if Levenshtein.distance(test_sequence, sequence) == distance:
            neighbors.append(test_sequence)
    return neighbors


entities.add_url_rule('/', view_func=EntityView.as_view('entities'))
entities.add_url_rule('/drop_db', view_func=DataBaseView.as_view('drop_db'))
entities.add_url_rule('/check_test', view_func=EntityTest.as_view('check_test'))
entities.add_url_rule('/add_learn', view_func=EntityAdd.as_view('add_learn'))
from .models import Entity as Records  # Если поместить вверху - можно получить циклические зависмости
