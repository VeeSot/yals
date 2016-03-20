import json

import flask
from flask import Blueprint, render_template
from flask.views import MethodView

entities = Blueprint('entities', __name__, template_folder='templates')


class EntityView(MethodView):
    def get(self):
        return render_template('index.html')


class EntityAdd(MethodView):
    def post(self, *args, **kwargs):
        from .models import Entity as Records
        data = json.loads(flask.request.data.decode())
        learn_data = data.get('learn_data')  # Всё содержание обучающего файла
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
        for data_set in raw_data_sets:
            Records.add(data_set)  # Сложим все записи в хранилище
        # После чего стоит пересчмитать данные и одновить укзатели на каналы которые мы считаем приоритетными
        Records.update_all()
        response = {'status': 'Database was updated'}
        return flask.jsonify(**response)


class EntityTest(MethodView):
    def post(self):
        response = {'status': 'Comprehension complete',
                    'pairs': [{'key': '0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0', 'value': 0},
                              {'key': '1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0', 'value': 1}]}
        return flask.jsonify(**response)


class DataBaseView(MethodView):
    def delete(self):
        from .models import Entity as Records
        Records.reset()
        response = {'status': 'Database was reset'}
        return flask.jsonify(**response)


# Register urls
entities.add_url_rule('/', view_func=EntityView.as_view('entities'))
entities.add_url_rule('/drop_db', view_func=DataBaseView.as_view('drop_db'))
entities.add_url_rule('/check_test', view_func=EntityTest.as_view('check_test'))
entities.add_url_rule('/add_learn', view_func=EntityAdd.as_view('add_learn'))
