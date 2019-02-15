#!/usr/bin/env python3
'''
MultiNER

MultiNER combines the output from four different
named-entity recognition packages into one answer.

https://github.com/KBNLresearch/MultiNER

Copyright 2013, 2019 Willem Jan Faber,
KB/National Library of the Netherlands.

To install most external dependencies using the following command:

    # python3 setup.py

For Stanford and Spotlight, see their own manuals on howto install those:

    https://nlp.stanford.edu/software/crf-faq.shtml#cc

    https://github.com/dbpedia-spotlight/dbpedia-spotlight/wiki/Run-from-a-JAR
    https://github.com/dbpedia-spotlight/dbpedia-spotlight/

Once installed (With wanted language models), run the webservices so MultiNER can contact those:

    $ cd /path/to/stanford-ner-2018-10-16
    $ java -mx400m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer \
           -outputFormat inlineXML -encoding "utf-8" \
           -loadClassifier dutch.crf.gz -port 9898

    $ cd /path/to/spotlight
    $ java --add-modules java.xml.bind -jar dbpedia-spotlight-1.0.0.jar \
                         nl http://localhost:9090/rest

    There is a small shell-script (run_external_ners.sh) available for this,
    modify it to your needs, if you change port's or want to use an external server,
    please keep them in sync with this file (STANFORD_HOST/PORT, SPOTLIGHT_HOST/PORT).

Language models spacy and polyglot:

    There is a big try catch block surrounding the invocation of polyglot,
    there is a good reason for that, I cannot seem to be able to force it to
    use a specific language, it will do a lang-detect and handle on that info.
    If the guessed language is not present, it will throw an exception.

    You can soft-link mutiple languages to other languages, to fool the software
    into using a wanted language, for example:

    $ cd ~/polyglot_data/ner2; mkdir af; ln -s ./nl/nl_ner.pkl.tar.bz2 ./af/af_ner.pkl.tar.bz2

    # apt-get install python-numpy libicu-dev
    $ pip install polyglot
    $ polyglot download embeddings2.nl

    $ python -m spacy download nl
    $ python -m spacy download de
    $ python -m spacy download fr
    $ python -m spacy download nl
    $ python -m spacy download en


Running test, and stable web-service:

    $ python3 ./ner.py

    This will run the doctest, if everything works, and external services are up,
    0 errors should be the result.

    $ gunicorn -w 10 web:application -b :8099

    Afther this the service can be envoked like this:

    $ curl -s localhost:8099/?url=http://resolver.kb.nl/resolve?urn=ddd:010381561:mpeg21:a0049:ocr

    If you expect to process a lot:

    # echo 1 > /proc/sys/ipv4/tcp_tw_recycle

    Else there will be no socket's left to process.
    
    
TODO:
hack this in somehow..:

from flask import abort, Flask, jsonify, request
from flair.models import SequenceTagger
from flair.data import Sentence
from segtok.segmenter import split_single

app = Flask(__name__)

tagger = SequenceTagger.load('ner-multi')

@app.route('/<text>', methods=['GET'])
def ner(text="Dit is een verhaal over dhr Willem Jan Faber."):
    global SequenceTagger
    sentences = [Sentence(sent, use_tokenizer=True) for sent in split_single(text)]
    tagger.predict(sentences)
    return jsonify([s.to_dict(tag_type='ner') for s in sentences])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8084)


    
    
'''
import json
import lxml.html
import requests
import operator

from flask import request, Response, current_app, Blueprint, render_template, flash, redirect
from lxml import etree

from corpora import times_test
from ner_packages.stanford import Stanford
from ner_packages.spotlight import Spotlight
from ner_packages.spacy import Spacy
from ner_packages.polyglot import Polyglot


def find_entities(text, language, context_len = 5):
    parsers = {"polyglot": Polyglot,
               "spacy": Spacy,
               "spotlight": Spotlight,
               "stanford": Stanford}

    # TODO: move KB logic to view and implement an API call to handle url functionality    
    # try:
        
    #     # parsed_text = ocr_to_dict(url)
    # except Exception:
    #     # result = {"error": "Failed to fetch %s" % url}
    #     resp = Response(response=json.dumps(result),
    #                     mimetype='application/json; charset=utf-8')
    #     return (resp)

    result_all = {}

    fresult = []
    for part in text:
        result = {}
        tasks = []

        # if manual:
        #     fresult.append(manual_find(manual,
        #                                parsed_text[part],
        #                                part,
        #                                context_len))

        for p in parsers:
            if (p == "stanford"):                
                tasks.append(parsers[p](
                    current_app.config.get('STANFORD_HOST'), 
                    current_app.config.get('STANFORD_PORT'), 
                    current_app.config.get('TIMEOUT'), 
                    text_input=text[part]))
            elif (p == "spotlight"):
                tasks.append(parsers[p](
                    current_app.config.get('SPOTLIGHT_HOST'), 
                    current_app.config.get('SPOTLIGHT_PORT'),
                    current_app.config.get('TIMEOUT'),
                    current_app.config.get('SPOTLIGHT_PATH'),
                    text_input=text[part]))
            else:
                tasks.append(parsers[p](text_input=text[part]))
            
            tasks[-1].start()

        for p in tasks:
            ner_result = p.join()
            result[list(ner_result)[0]] = ner_result[list(ner_result)[0]]

        result_all[part] = intergrate_results(result,
                                              part,
                                              text[part],
                                              context_len)

    for part in result_all:
        if result_all[part]:
            for item in result_all[part]:
                fresult.append(item)

    result = {"entities": fresult}

    # result = json.dumps({"entities": fresult,
    #                      "text": parsed_text})

    TEST_OUTPUT = '/home/alexhebing/Projects/placenamedisambiguation/test_files/output/entities.json'
    with open(TEST_OUTPUT, 'w+') as file:    
        file.write(json.dumps({"entities": fresult}, indent=4, sort_keys=True))

    resp = Response(response=result,
                    mimetype='application/json; charset=utf-8')

    return (result)



def context(text_org, ne, pos, context=5):
    '''
        Return the context of an NE, based on abs-pos,
        if there are 'context-tokens' in the way,
        skip those.

        Current defined context-tokens:
        ”„!,'\",`<>?-+"
    '''
    CONTEXT_TOKENS = "”„!,'\",`<>?-+\\"

    leftof = text_org[:pos].strip()
    l_context = " ".join(leftof.split()[-context:])

    rightof = text_org[pos + len(ne):].strip()
    r_context = " ".join(rightof.split()[:context])

    ne_context = ne

    try:
        if l_context[-1] in CONTEXT_TOKENS:
            ne_context = l_context[-1] + ne_context
    except Exception:
        pass

    try:
        if r_context[0] in CONTEXT_TOKENS:
            ne_context = ne_context + r_context[0]
    except Exception:
        pass

    return l_context, r_context, ne_context


def translate(input_str):
        '''
            Translate the labels to one-form-fits-all (that is also human-readable).
        '''
        if input_str == "ORG":
            return 'ORGANIZATION'
        if input_str == "PER":
            return 'PERSON'
        if input_str == "MISC":
            return 'OTHER'
        if input_str == "LOC":
            return 'LOCATION'
        return input_str


def intergrate_results(result, source, source_text, context_len):
    new_result = {}
    res = {}

    for ne in result.get("stanford"):
        res = {}
        res["count"] = 1
        res["ne"] = ne.get("ne")
        res["ner_src"] = ["stanford"]
        res["type"] = {ne.get("type"): 1}
        res["pref_type"] = ne.get("type")
        new_result[ne.get("pos")] = res

    for ne in result.get("spotlight"):
        if not ne.get("pos") in res:
            res = {}
            res["count"] = 1
            res["ne"] = ne.get("ne")
            res["ner_src"] = ["spotlight"]
            res["type"] = {ne.get("type"): 1}
            res["pref_type"] = ne.get("type")
            new_result[ne.get("pos")] = res
        else:
            new_result[ne.get("pos")]["count"] += 1
            new_result[ne.get("pos")]["ner_src"].append("spotlight")

            if not ne.get("type") in new_result[ne.get("pos")]["type"]:
                new_result[ne.get("pos")]["type"][ne.get("type")] = 1
            else:
                new_result[ne.get("pos")]["type"][ne.get("type")] += 1

    parsers = ["spacy", "polyglot"]

    for parser in parsers:
        for ne in result.get(parser):
            # Both spacy and polyglot return abbreviations as type (e.g. PER)
            # translate these into the same as Stanford (e.g. PERSON)
            ne_type = translate(ne.get("type"))
            
            if ne.get("pos") in new_result:

                if parser in new_result[ne.get("pos")]["ner_src"]:
                    continue

                new_result[ne.get("pos")]["count"] += 1
                new_result[ne.get("pos")]["ner_src"].append(parser)

                if ne_type in new_result[ne.get("pos")]["type"]:
                    new_result[ne.get("pos")]["type"][ne_type] += 1
                else:
                    new_result[ne.get("pos")]["type"][ne_type] = 1

                if not ne.get("ne") == new_result[ne.get("pos")].get("ne"):
                    new_result[ne.get("pos")]["alt_ne"] = ne.get("ne")

            else:
                new_result[ne.get("pos")] = {
                    "count": 1,
                    "ne": ne.get("ne"),
                    "ner_src": [parser],
                    "type": {ne_type: 1}}

    final_result = []
    for ne in new_result:
        if new_result[ne].get("pref_type") or \
                len(new_result[ne].get("ner_src")) == 2:
            if "pref_type" in new_result[ne]:
                ne_type = max_class(new_result[ne]["type"],
                                    new_result[ne]["pref_type"])
                new_result[ne].pop("pref_type")
            else:
                ne_type = max_class(new_result[ne]["type"],
                                    list(new_result[ne]["type"])[0])

            new_result[ne]["types"] = list(new_result[ne]["type"])
            new_result[ne]["type"] = { ne_type[0] : 1}
            new_result[ne]["type_certainty"] = ne_type[1]

            new_result[ne]["left_context"], \
            new_result[ne]["right_context"], \
            new_result[ne]["ne_context"] = context(source_text,
                                                   new_result[ne]["ne"],
                                                   ne,
                                                   context_len)
            new_result[ne]["pos"] = ne
            new_result[ne]["source"] = source

            final_result.append(new_result[ne])

    final_result = sorted(final_result, key=operator.itemgetter('pos'))

    return final_result


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


def max_class(input_type={"LOC": 2, "MISC": 3}, pref_type="LOC"):
    mc = max(input_type, key=input_type.get)

    if input_type.get(mc) == 1:
        mc = pref_type
        sure = 1
    if input_type.get(mc) == 2:
        sure = 2
    if input_type.get(mc) == 3:
        sure = 3
    if input_type.get(mc) == 4:
        sure = 4

    return(mc, sure)


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


def test_all():
    '''
    Example usage:

    >>> parsers = {"polyglot": Polyglot,
    ...            "spacy": Spacy,
    ...            "stanford": Stanford,
    ...            "spotlight": Spotlight}

    >>> url = [EXAMPLE_URL]
    >>> parsed_text = ocr_to_dict(url[0])

    >>> tasks = []
    >>> result = {}

    >>> for p in parsers:
    ...     tasks.append(parsers[p](parsed_text=parsed_text["p"]))
    ...     tasks[-1].start()

    >>> import time
    >>> time.sleep(1)

    >>> for p in tasks:
    ...     ner_result = p.join()
    ...     result[list(ner_result)[0]] = ner_result[list(ner_result)[0]]

    >>> from pprint import pprint
    >>> pprint(intergrate_results(result, "p", parsed_text["p"], 5)[-1])
    {'count': 2,
     'left_context': 'als wie haar nadert streelt:',
     'ne': 'René',
     'ne_context': 'René',
     'ner_src': ['spacy', 'polyglot'],
     'pos': 5597,
     'right_context': 'genoot van zijn charme als',
     'source': 'p',
     'type': 'person',
     'type_certainty': 2,
     'types': ['person']}
    '''
    return


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=True)
