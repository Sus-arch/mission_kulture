from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, TextAreaField, RadioField
from wtforms.validators import DataRequired


class AddObject(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    about = TextAreaField('Описание')
    reester_number = StringField('Номер в реестре', validators=[DataRequired()])
    region = StringField('Регион', validators=[DataRequired()])
    full_address = StringField('Полный адрес')
    category = RadioField('Выберите категорию', choices=[
        ('Местного (муниципального) значения', 'Местного (муниципального) значения'),
        ('Федерального значения', 'Федерального значения'),
        ('Регионального значения', 'Регионального значения')
    ], validators=[DataRequired()])
    kind = RadioField('Вид объекта', choices=[
        ('Ансамбль', 'Ансамбль'),
        ('Памятник', 'Памятник')
    ], validators=[DataRequired()])
    unesco = BooleanField('Принадлежность к Юнеско')
    is_value = BooleanField('Особо ценный объект')
    coords = StringField('Координаты')
    submit = SubmitField('Добавить объект')
