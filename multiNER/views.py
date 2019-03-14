import json
import requests
import lxml
from flask import request, Response, current_app, Blueprint, render_template, flash, redirect, abort


from .forms import NerForm
from .ner import find_entities, context


bp = Blueprint('ner', __name__, url_prefix='/ner')

@bp.route('/', methods=['GET', 'POST'])
def index():
    form = NerForm()
    if form.validate_on_submit():
        text = form.text.data.replace('\r', ' ').replace('\n', ' ')
        entities = find_entities({'title': form.title.data, 'text': text}, form.language.data)
        return render_template('multiNER/results.html', text=text, entities=entities)
        
    return render_template('multiNER/index.html', form=form)


@bp.route('/collect_from_text', methods=['GET'])
def collect_from_text():    
    if not request.json:
        abort(400)
    
    # Validate user's input
    jsonData = request.get_json()

    if not 'text' in jsonData:
        abort(400, 'text is required')
    
    # extract input
    text = jsonData['text']

    # TODO: validate text? length / encoding / whatever

    if not 'language' in jsonData:
        language = 'nl'
    else:
        language = jsonData['language']

    if not 'title' in jsonData:
        title = None
    else:
        title = jsonData['title']

    if not 'context_len' in jsonData:
        context_len = 5
    else:
        context_len = jsonData['context_len']

    entities = find_entities({'title': title, 'text': text}, language, context_len)
    
    resp = Response(response=json.dumps(entities), mimetype='application/json; charset=utf-8')
    return (resp)



@bp.route('/collect_from_kb_url')
def collect_from_kb_url():
    url = request.args.get('url')
    manual = request.args.get('manual')
    context_len = request.args.get('context')
    
    if not context_len:
        context_len = 5
    else:
        context_len = int(context_len)

    if not url:
        result = {"error": "Missing argument ?url=%s" % current_app.config.get('EXAMPLE_URL')}
    else:
        result = {}
        
        parsed_text = ocr_to_dict(url)
        result = find_entities(parsed_text, 'nl', context_len)
        
        manual_result = []

        if manual:
            for part in parsed_text:
                manual_result.append(manual_find(manual, parsed_text[part],part, context_len))

            result['entities']['manual'] = manual_result
    
    resp = Response(response=json.dumps(result), mimetype='application/json; charset=utf-8')
    return (resp)


def ocr_to_dict(url):
    '''
        Fetch some OCR from the KB / Depher newspaper collection,
        remove the XML-tags, and put it into a dictionary:

        >>> EXAMPLE_URL = "http://resolver.kb.nl/resolve?"
        >>> EXAMPLE_URL += "urn=ddd:010381561:mpeg21:a0049:ocr"
        >>> ocr_to_dict(EXAMPLE_URL).get("title")
        'EERSTE HOOFDSTUK'
    '''

    done = False
    retry = 0

    while not done:
        try:
            req = requests.get(url, timeout=current_app.config.get('TIMEOUT'))
            if req.status_code == 200:
                done = True
            retry += 1
            if retry > 50:
                done = True
        except Exception:
            done = False

    text = req.content
    text = text.decode('utf-8')

    parser = lxml.etree.XMLParser(ns_clean=False,
                                  recover=True,
                                  encoding='utf-8')

    xml = lxml.etree.fromstring(text.encode(), parser=parser)

    parsed_text = {}

    for item in xml.iter():
        if not item.text:
            continue

        item.text = item.text.replace('&', '&amp;')
        item.text = item.text.replace('>', '&gt;')
        item.text = item.text.replace('<', '&lt;')

        if item.tag == 'title':
            if "title" not in parsed_text:
                parsed_text["title"] = []
            parsed_text["title"].append(item.text)
        else:
            if "p" not in parsed_text:
                parsed_text["p"] = []
            parsed_text["p"].append(item.text)

    for part in parsed_text:
        parsed_text[part] = "".join(parsed_text[part])

    return parsed_text


def manual_find(input_str, source_text, source, context_len):
    '''
        Find occurrence of an 'ne' and
        get the left and right context.
    '''

    result = {}

    pos = source_text.find(input_str)
    result["pos"] = pos
    result["ne"] = input_str
    result["source"] = source
    result["type"] = 'manual'

    if not pos == -1:
        result["left_context"],
        result["right_context"],
        result["ne_context"] = context(source_text,
                                       input_str,
                                       pos,
                                       context_len)
    else:
        result["left_context"] = result["right_context"] = ''
        result["ne_context"] = input_str

    return result

