from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class ProjectsForm(FlaskForm):
    heading = StringField('Заголовок работы', validators=[DataRequired()])
    annotation = TextAreaField('Аннотация', validators=[DataRequired()])

    image = FileField('png')

    submit = SubmitField('Применить')
