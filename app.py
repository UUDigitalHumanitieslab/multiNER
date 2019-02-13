#!/usr/bin/env python3

import logging
from flask import Flask

from multiNER import config
from multiNER.ner import api


def flask_app(cfg=config):
    app = Flask(__name__)
    app.config.from_object(cfg)
    app.register_blueprint(api)
    return app

app = flask_app(config)

