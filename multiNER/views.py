from flask import request, Response, current_app, Blueprint, render_template, flash, redirect
import json

from .forms import NerForm
from .ner import find_entities


bp = Blueprint('ner', __name__, url_prefix='/ner')

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = NerForm()
    if form.validate_on_submit():
        text = form.text.data.replace('\r', ' ').replace('\n', ' ')
        entities = find_entities({'title': form.title.data, 'p': text}, form.language.data)
        return render_template('multiNER/results.html', text=text, entities=entities)
        
    return render_template('multiNER/index.html', form=form)


@bp.route('/find/')
def collect():
    url = request.args.get('url')
    manual = request.args.get('ne')
    context_len = request.args.get('context')

    if not context_len:
        context_len = 5
    else:
        context_len = int(context_len)

    if not url:
        result = {"error": "Missing argument ?url=%s" % current_app.config.get('EXAMPLE_URL')}
        resp = Response(response=json.dumps(result),
                        mimetype='application/json; charset=utf-8')
        return (resp)

def to_pretty_json(value):
    return json.dumps(value, sort_keys=True, indent=4, separators=(',', ': '))
