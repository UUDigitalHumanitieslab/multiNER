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

    ner_config = get_configuration(jsonData['configuration'])
    
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

    if not 'leading_packages' in config:
        config['leading_packages'] = ['stanford', 'spotlight']

    if not 'other_packages_min' in config:
        config['other_packages_min'] = 2
    
    if 'type_preference' in config:
        converted_keys = {}
        for key, type in config['type_preference'].items():
            converted_keys[int(key)] = type

        config['type_preference'] = converted_keys
    else:
        config['type_preference'] = {1: 'LOCATION',
                                     2: 'PERSON', 3: 'ORGANIZATION', 4: 'OTHER'}

    return Configuration(
        config['language'], 
        config['context_length'], 
        config['leading_packages'], 
        config['other_packages_min'], 
        config['type_preference'])
