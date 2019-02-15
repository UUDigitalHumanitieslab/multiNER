from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, RadioField
from wtforms.validators import DataRequired

class NerForm(FlaskForm):
    title = StringField('Title', default="test", validators=[DataRequired()])
    text = TextAreaField('Text', render_kw={"rows": 15, "cols": 100}, validators=[DataRequired()])
    language = RadioField('Language', choices = [('en', 'English'),('it', 'Italian'), ('nl', 'Dutch')], default='en')
    submit = SubmitField('Find entities')
