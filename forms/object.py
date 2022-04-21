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
        ('1', 'Местного (муниципального) значения'),
        ('2', 'Федерального значения'),
        ('3', 'Регионального значения')
    ], validators=[DataRequired()])
    kind = RadioField('Вид объекта', choices=[
        ('1', 'Ансамбль'),
        ('2', 'Памятник')
    ], validators=[DataRequired()])
    unesco = BooleanField('Принадлежность к Юнеско', validators=[DataRequired()])
    is_valuable = BooleanField('Особо ценный объект', validators=[DataRequired()])
    submit = SubmitField('Добавить объект')
