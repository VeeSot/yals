import flask
from flask import Blueprint, render_template, flash
from flask.views import MethodView

entities = Blueprint('entities', __name__, template_folder='templates')


class EntityView(MethodView):
    def get(self):
        return render_template('index.html')


class EntityAdd(MethodView):
    def post(self):
        response = {'status': 'Database was updated'}
        return flask.jsonify(**response)


class EntityTest(MethodView):
    def post(self):
        response = {'status': 'Comprehension complete',
                    'pairs': [{'key': '0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0', 'value': 0},
                              {'key': '1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0', 'value':1}]}
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
