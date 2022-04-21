from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class AddCommentForm(FlaskForm):
    text = TextAreaField('Ваш комментарий', validators=[DataRequired()])
    obj_id = IntegerField()
    submit = SubmitField('Добавить комментарий', validators=[DataRequired()])
