import json
from typing import List

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
                channel = "Канал неизвестен"
            pairs.append({'key': data_set, 'value': channel})
        response = {'status': 'Comprehension complete', 'pairs': pairs}
        return flask.jsonify(**response)


class DataBaseView(MethodView):
    def delete(self):
        Records.reset()
        response = {'status': 'Database was reset'}
        return flask.jsonify(**response)


def get_request_data() -> List[str]:
    """Получаем данные из запроса,чистим и возвращаем набор данных
    :param data_type: Тип данных.Могут быть обучающими или тестируемыми
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
            # Следующей строчкой пойдут обучающие данные.Пора прерваться
            break
    raw_data_sets = data_sets[pointer:]
    raw_data_sets = filter(lambda x: x != '', raw_data_sets)  # Игнорируем пустые строки
    return raw_data_sets


entities.add_url_rule('/', view_func=EntityView.as_view('entities'))
entities.add_url_rule('/drop_db', view_func=DataBaseView.as_view('drop_db'))
entities.add_url_rule('/check_test', view_func=EntityTest.as_view('check_test'))
entities.add_url_rule('/add_learn', view_func=EntityAdd.as_view('add_learn'))
from .models import Entity as Records  # Если поместить вверху - можно получить циклические зависмости
