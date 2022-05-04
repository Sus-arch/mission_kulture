from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, RadioField, FileField, IntegerField
from wtforms.validators import DataRequired, Optional


class AddObject(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    about = TextAreaField('Описание')
    about_file = FileField('Или приложите файл с текстом')
    reester_number = StringField('Номер в реестре', validators=[DataRequired()])
    region = IntegerField('Регион', validators=[DataRequired()])
    full_address = StringField('Полный адрес')
    category = RadioField('Выберите категорию', choices=[
        (4, 'Местного (муниципального) значения'),
        (1, 'Федерального значения'),
        (2, 'Регионального значения')
    ], validators=[DataRequired()])
    kind = RadioField('Вид объекта', choices=[
        (2, 'Ансамбль'),
        (1, 'Памятник'),
        (3, 'Достопримечательное место')
    ], validators=[DataRequired()])
    unesco = BooleanField('Принадлежность к Юнеско')
    is_value = BooleanField('Особо ценный объект')
    coords = StringField('Координаты')
    submit = SubmitField('Добавить объект')


class FindObjectForm(FlaskForm):
    name = StringField('Название', validators=[Optional()])
    reester_number = StringField('Номер в реестре', validators=[Optional()])
    region = IntegerField('Регион', validators=[Optional()])
    category = RadioField('Выберите категорию', choices=[
        (4, 'Местного (муниципального) значения'),
        (1, 'Федерального значения'),
        (2, 'Регионального значения')], validators=[Optional()])
    kind = RadioField('Вид объекта', choices=[
        (2, 'Ансамбль'),
        (1, 'Памятник'),
        (3, 'Достопримечательное место')], validators=[Optional()])
    unesco = BooleanField('Принадлежность к Юнеско', validators=[Optional()])
    is_value = BooleanField('Особо ценный объект', validators=[Optional()])
    submit = SubmitField('Поиск')

    def clear(self):
        self.region.data = None