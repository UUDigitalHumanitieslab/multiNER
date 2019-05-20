import json
import requests
import lxml
from flask import request, Response, current_app, Blueprint, render_template, flash, redirect, abort


from .forms import NerForm
from .ner import MultiNER, Configuration

bp = Blueprint('ner', __name__, url_prefix='/ner')


@bp.route('/', methods=['GET', 'POST'])
def index():
    form = NerForm()
    if form.validate_on_submit():

        text = form.text.data.replace('\r', ' ').replace('\n', ' ')

        ner_config = Configuration(
            form.language.data,
            5,
            ['stanford', 'spotlight'],
            2,
            {1: 'LOCATION', 2: 'PERSON', 3: 'ORGANIZATION', 4: 'OTHER'})

        multiner = MultiNER(current_app.config, ner_config)
        input = {'title': form.title.data, 'text': text}
        entities_per_part = multiner.find_entities(input)

        return render_template('multiNER/results.html', text=text, entities=entities_per_part)

    return render_template('multiNER/index.html', form=form)


@bp.route('/collect_from_text', methods=['GET'])
def collect_from_text():
    if not request.json:
        abort(400)

    # Validate user's input
    jsonData = request.get_json()

    if not 'text' in jsonData:
        abort(400, 'text is required')

    # extract input and validate
    text = jsonData['text']

    if not 'title' in jsonData:
        title = None
    else:
        title = jsonData['title']

    if 'configuration' in jsonData:
        validated_config = validate_configuration(jsonData['configuration'])
        ner_config = get_configuration(validated_config)
    else:
        ner_config = get_configuration({})

    multiner = MultiNER(current_app.config, ner_config)

    input = {'title': title, 'text': text}
    entities_per_part = multiner.find_entities(input)

    resp = Response(response=json.dumps(entities_per_part),
                    mimetype='application/json; charset=utf-8')
    return (resp)


def get_configuration(config):
    if not 'language' in config:
        config['language'] = 'en'

    if not 'context_length' in config:
        config['context_length'] = 5

    if not 'leading_ner_packages' in config:
        config['leading_ner_packages'] = ['stanford', 'spotlight']

    if not 'other_packages_min' in config:
        config['other_packages_min'] = 2

    if 'type_preference' in config:
        converted_keys = {}
        for key, type in config['type_preference'].items():
            converted_keys[int(key)] = type

        config['type_preference'] = converted_keys
    else:
        config['type_preference'] = {
            1: 'LOCATION',
            2: 'PERSON',
            3: 'ORGANIZATION',
            4: 'OTHER'
        }

    return Configuration(
        config['language'],
        config['context_length'],
        config['leading_ner_packages'],
        config['other_packages_min'],
        config['type_preference'])


def validate_configuration(config):
    if 'language' in config:
        if not config['language'] in ['en', 'it', 'nl']:
            abort(400, "language '{}' is not supported".format(
                config['language']))

    if 'context_length' in config:
        if not isinstance(config['context_length'], int):
            abort(400, "context_length should be an integer")
        if 0 > config['context_length'] > 15:
            abort(400, "context_length should be a number between 0 and 15")

    if 'leading_ner_packages' in config:        
        for package in config['leading_ner_packages']:
            if not package in ['stanford', 'spotlight', 'spacy', 'polyglot']:
                abort(400, "package '{}' is not supported".format(package))

    if 'other_packages_min' in config:
        if 1 > config['other_packages_min'] or config['other_packages_min'] > 4:
            abort(400, "other_packages_min should be a number between 1 and 4")

    if 'type_preference' in config:
        if not isinstance(config['type_preference'], dict):
            abort(400, "type_preference should be a dictionary")

        for key, value in config['type_preference']:
            if not key in ['1', '2', '3', '4']:
                abort(400, "Key '{}' is invalid in type_preference".format(key))

            if not value in ['LOCATION', 'PERSON', 'ORGANIZATION', 'OTHER']:
                abort(400, "Value '{}' is invalid in type_preference".format(value))

    return config
