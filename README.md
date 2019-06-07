# multiNER

MultiNER is a webservice that combines the output from four different [named-entity recognition](https://en.wikipedia.org/wiki/Named-entity_recognition) packages into one answer. This impementation is based on the [multiNER software implemented by the KB](https://github.com/KBNLresearch/multiNER), where it is part of the [DAC  project](https://github.com/KBNLresearch/dac) (Entity linker for the Dutch historical newspaper collection of the National Library of the Netherlands).

The following packages are used:

    - Stanfor NER (https://nlp.stanford.edu/software/CRF-NER.shtml)
    - DBpedia Spotlight (https://www.dbpedia-spotlight.org/)
    - spaCy (https://spacy.io/)
    - polyglot (http://polyglot.readthedocs.io/)

## Overview

MultiNER is a Flask application that exposes one method (`collect_from_text`) that returns the entities found in a text based on the Named Entities suggested by the various NER packages. These packages are its main dependencies. Stanford and DbPedia Spotlight are Java applications that run as webservices, whereas Spacy and Polyglot are Python packages.

MultiNER returns entities of four types: LOCATION, PERSON, ORGANIZATION and OTHER. All entities suggested by the various ner packages are translated into these four.

One of the nice features of multiNER is that the user can configure the weight of the different packages for each API call. See below for details.

## Prerequisites

### Stanford

#### Info and download

More information and download link can be found in [this article](https://nlp.stanford.edu/software/CRF-NER.html).

#### Models

Stanford by default includes some English models (in the folder `classifiers`). Note that the Dutch model can be found in Surfdrive: '/DigitalHumanitiesLabatUU/PlaceNameDisambiguation/multiNER/stanford/dutch.tar.gz'. Simply untar and supply dutch.gz as `<themodelyouwanttouse>`.

#### Run

```java
java -mx400m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer            -outputFormat inlineXML -encoding "utf-8" -loadClassifier classifiers/<themodelyouwanttouse>.gz -port <whateverportyoulike>
```

For example, with the complete English model loaded and running at port 9899:

```java
java -mx400m -cp stanford-ner.jar edu.stanford.nlp.ie.NERServer            -outputFormat inlineXML -encoding "utf-8" -loadClassifier classifiers/english.all.3class.distsim.crf.ser.gz -port 9899
```

#### Access

Accessing the Stanford webservice directly is done via the [Telnet protocol](https://en.wikipedia.org/wiki/Telnet). For example:

```python
import telnetlib

done = False
retry = 0
max_retry = 10

while not done and retry < max_retry:
    try:
        conn = telnetlib.Telnet(host='<hostname>', port=<port>, timeout=1000)
        done = True
    except Exception as e:
        print(e)
        retry += 1

text = 'a text with lots of nice entities'
text = text.encode('utf-8') + b'\n'
conn.write(text)
result = conn.read_all().decode('utf-8')
conn.close()

```

### DbPedia Spotlight

#### Info and download

More info on the DbPedia API can be found [here](https://www.dbpedia-spotlight.org/api). Note that it returns a plurality of types for each entity (e.g. 'DbPlace', 'DbLocation', 'Administrative Region', 'Governmental Region', etc)

Downloads are available from [here](https://sourceforge.net/projects/dbpedia-spotlight/files/spotlight/)

Models:
Models for DbPedia are available [here](https://sourceforge.net/projects/dbpedia-spotlight/files/)

Download the Dutch model:

```bash
wget https://sourceforge.net/projects/dbpedia-spotlight/files/2016-10/nl/model/nl.tar.gz/download
```

#### Run

Java above JDK version 8 (i.e. 9 and higher) do not include all required Java modules. (see [this SO answer](https://stackoverflow.com/a/43574427)). Therefore add `--add-modules java.se.ee` when you start the webservice:

```java
java --add-modules java.se.ee -jar dbpedia-spotlight-1.0.0.jar models/<whatevermodelyouwanttouse> http://<hostname>:<portnumber>/rest
```

For example, run with the Italian model on localhost, port 2222:

```java
java --add-modules java.se.ee -jar dbpedia-spotlight-1.0.0.jar models/it http://localhost:2222/rest
```

#### Access

You can access the DbPedia webservice via HTTP, it even works in your browser:

```
http://localhost:2222/rest/annotate/?text='Another pretty text with some incredibly relevant entities'
```

Of course you can always use some other tool to make the request for you, like [curl](https://curl.haxx.se/) or [Postman](https://www.getpostman.com/), or whatever you like.

### Spacy

#### Info and download

Spacy is a Python package and can be installed via Pip. Setting up the multiNER application will automatically install Spacy for you. Note that installing spacy takes a looooooong time.

#### Models

Spacy models are Python packages as well. These are installed automatically as well, but there is something special about them.
As [the Spacy documentation specifies](https://spacy.io/usage/models#production), they are loaded directly from Github (i.e. they are in `requirements.txt` as (for example) `https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.1.0/en_core_web_sm-2.1.0.tar.gz#egg=en_core_web_sm`)

#### Run and Access

Spacy is run and accessed from the multiNER code. See the documentation if you need to consume it yourself.

### Polyglot

#### Info and download

Polyglot, like Spacy, is a Python package and can be installed via Pip. Setting up the multiNER application will automatically install Spacy for you.

It is somewhat special in that it tries to guess the language of the text it is being supplied (although you can suggest a language). This potentially leads to errors if models are not installed for the language Polyglot thinks it is NER-ing.

#### Prerequisites

Installing Polyglot is dependent on the presence of the package `libicu-dev` (`sudo apt install libicu-dev`). If you do not have this package installed, you will get errors like `Command "python setup.py egg_info" failed with error code 1 in /tmp/tmp3wehjwuobuild/pyicu/` when installing via pip (or compiling with pip-tools). This requirement that this error comes from is pyicu. More solutions to this problem (i.e. for other OSs) [in this SO post](https://stackoverflow.com/questions/40940188/error-installing-pip-pyicu)


#### Models

Polyglot models are Python packages, but these are not automatically installed. You need to manually download them. For example, Dutch:

```python
polyglot download embeddings2.nl
polyglot download ner2.nl
```

Find all available models [here](https://polyglot.readthedocs.io/en/latest/Download.html#langauge-task-support)

#### Run and Access

Polyglot is run and accessed from the multiNER code. See the documentation if you need to consume it yourself.

## Installation

Once you have the Stanford and DbPedia Spotlight webservices up and running, you can set up multiNER itself.

Setup a virtualenv with Python 3.4

```bash
virtualenv .env -p python3.4 --prompt "(multiner) "
```

Enter the virtualenv: `source .env/bin/activate`

Install requirements: `pip install -r requirements.txt`

Set Flask variables and run:

```bash
export FLASK_APP=app.py
export FLASK_DEBUG=1
flask run
```

## Tests

The multiNER application includes a bunch of unit tests. To run these, install pytest into your virtualenv (`pip install pytest`) and run: `pytest`.


## Usage

### Request

You should now have a webservice running at `http://localhost:5000/ner/collect_from_text`. It takes three parameters, of which one is required:

| Name          | Required | Info                                 |
| ------------- | -------- | ------------------------------------ |
| title         | False    | If provided this will also be NER-ed |
| text          | True     | The main text to be NER-ed           |
| configuration | False    | If False, use default configuration  |

Example request:

```json
{
    "title": "Mooi tekstje",
    "text": "Utrecht ligt ver weg van Rotterdam",
    "configuration": {
        "language": "nl",
        "context_length": 3,
        "leading_ner_packages": [
                "stanford",
                "spotlight"
            ],
        "other_packages_min": 2
    }
}
```

#### Configuration

The configuration parameter gives the user the ability to configure how multiNER creates one Named Entity from the sudggestions made by the various NER packages. It allows for several settings to be set:

| Setting  | Info                     | Allowed values   | Default |
| -------- | ------------------------ | ---------------- | ------- |
| language | The language of the text | 'nl', 'en', 'it' | 'en'    |
| context_length | Number of words to collect left and write of each entity | 0 to 15 | 5
| leading_ner_packages | List of packages whose suggestions should always be included | 'stanford', 'spotlight', 'spacy', 'polyglot' | ['stanford', 'spotlight' ]
| other_packages_min | The minimum number of non-leading-packages required to suggest a Named Entity before it is included. E.g. if only Spacy suggest that a particular piece of text is a LOCATION and this setting's value is 2, the suggestion will be ignored. | 1 to 4 | 2
| type_preference | A dictionary with format `{<number>:<type>}` specifying which type is preferred when more than one type is suggested. Note that this determines which type an entity is if there is no agreement (i.e. all packages suggest a different type). Currently, 'type_preference' is not integrated with 'leading_ner_packages', i.e. it just considers the different types, not which package suggested it. | Keys: [1, 2, 3, 4], Values: ['LOCATION', 'PERSON', 'ORGANIZATION', 'OTHER'] | { 1: 'LOCATION', 2: 'PERSON', 3: 'ORGANIZATION', 4: 'OTHER' }

### Response

#### General form

MultiNER returns a JSON object with the following basic structure:

```json
    {
        "title": {
            "text": "The title",
            "entities": [
                // A list of the entities found
            ]
        }
    },
    {
        "text": {
            "text": "The title",
            "entities": [
                // A list of the entities found
            ]
        }
    }
```

That is to say it returns an embedded JSON object for each part you send: the title and the text. Each of these contains the original text and the entities found in that text.

#### Entities

MultiNER returns Named Entities in which the suggestions from the various NER packages are integrated. Therefore, each entity has some special fields pertaining to the details of the integration, such as 'type_certainty', and 'alt_nes'. In addition, a list of all types suggested is also present.

| Attribute | Info |
| --- | --- |
| pos | The start index of the entity in the text |
| ne | The actual named entity, i.e. the text for which a type is suggested |
| alt_nes | Alternative entities suggested for the same position in the text. For example, Stanford might suggest 'Angelina Jolie', whereas 'spacy might suggest 'Angelina'. Such double data is stored here. Note that it is also possible that an `alt_ne` does not have the same starting index. For example, Polyglot may find 'Universiteit Utrecht' (an ORGANIZATION), and Spotlight suggests 'Utrecht' (a LOCATION). As long as Spotlight is referring to the same positions in the text, this is also considered an 'alt_ne'. |
| right_context | A configurable number of words to the right of the entity |
| left_context | A configurable number of words to the left of the entity |
| count | The number of NER packages that suggest this entity |
| type | The type of the entity found. Based on 'type_preference' if there is no agreement between the various NER packages. |
| type_certainty | The number of packages that suggested the entity's type. |
| ner_src | The packages that suggested this entity |
| types | A list of the types suggested |

Example response:

```json
    "count": 3,
    "type_certainty": 2,
    "type": "PERSON",
    "right_context": "zich mij te vragen, of",
    "left_context": "op zijn allerlaatst verwaardigde mevrouw",
    "pos": 1324,
    "ne_context": "Manchon",
    "ne": "Manchon",
    "ner_src": [
        "stanford",
        "spacy",
        "polyglot"
    ],
    "types": [
        "PERSON",
        "LOCATION"
    ]
```
