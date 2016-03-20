from flask import Blueprint, render_template
from flask.views import MethodView

entities = Blueprint('entities', __name__, template_folder='templates')


class Entity(MethodView):
    def get(self):
        return render_template('index.html')


# Register urls
entities.add_url_rule('/', view_func=Entity.as_view('entities'))
