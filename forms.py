from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, FloatField, SelectField, EmailField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask_wtf.file import FileField, FileRequired, FileAllowed

# Formulário de registro de usuário
class RegistroForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired(), Length(min=4, max=64)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=128)])
    fullname = StringField('Nome Completo', validators=[DataRequired(), Length(max=128)])
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=14)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

# Formulário de login de usuário
class LoginForm(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

# Formulário para edição de bem
class EditarBemForm(FlaskForm):
    nome = StringField('Nome do Bem', validators=[DataRequired(), Length(max=128)])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    data_aquisicao = DateField('Data de Aquisição', format='%Y-%m-%d', validators=[DataRequired()])
    valor = FloatField('Valor', validators=[DataRequired()])
    numero_serie = StringField('Número de Série', validators=[DataRequired(), Length(max=64)])
    estado = SelectField('Estado', choices=[('Disponível', 'Disponível'), ('Em uso', 'Em uso'), ('Em manutenção', 'Em manutenção'), ('Descartado', 'Descartado')], validators=[DataRequired()])
    foto = FileField('Foto do Bem', validators=[Optional(), FileAllowed(['jpg', 'png'], 'Apenas imagens são permitidas!')])  # Adiciona o campo de foto
    submit = SubmitField('Salvar Alterações')

# Formulário para registrar entrada de bem
class RegistrarEntradaForm(FlaskForm):
    nome = StringField('Nome do Bem', validators=[DataRequired(), Length(max=128)])
    descricao = TextAreaField('Descrição', validators=[DataRequired()])
    data_aquisicao = DateField('Data de Aquisição', format='%Y-%m-%d', validators=[DataRequired()])
    valor = FloatField('Valor', validators=[DataRequired()])
    numero_serie = StringField('Número de Série', validators=[DataRequired(), Length(max=64)])
    estado = SelectField('Estado', choices=[('Disponível', 'Disponível'), ('Em uso', 'Em uso'), ('Em manutenção', 'Em manutenção'), ('Descartado', 'Descartado')], validators=[DataRequired()])
    foto = FileField('Foto do Bem', validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Apenas imagens são permitidas!')])
    submit = SubmitField('Registrar Entrada')

# Formulário para registrar saída de bem
class RegistrarSaidaForm(FlaskForm):
    bem_id = StringField('ID do Bem', validators=[DataRequired()])
    descricao = TextAreaField('Descrição da Saída', validators=[Optional()])
    data = DateField('Data da Saída', format='%Y-%m-%d', validators=[DataRequired()])
    destino = StringField('Destino', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('Registrar Saída')

# Formulário para registrar transferência de bem
class RegistrarTransferenciaForm(FlaskForm):
    bem_id = StringField('ID do Bem', validators=[DataRequired()])
    descricao = TextAreaField('Descrição da Transferência', validators=[Optional()])
    data = DateField('Data da Transferência', format='%Y-%m-%d', validators=[DataRequired()])
    destino = StringField('Destino', validators=[DataRequired(), Length(max=128)])
    submit = SubmitField('Registrar Transferência')

# Formulário para relatórios
class RelatoriosForm(FlaskForm):
    tipo_relatorio = SelectField('Tipo de Relatório', choices=[('Entrada', 'Entrada'), ('Saída', 'Saída'), ('Transferência', 'Transferência')], validators=[DataRequired()])
    data_inicio = DateField('Data Início', format='%Y-%m-%d', validators=[Optional()])
    data_fim = DateField('Data Fim', format='%Y-%m-%d', validators=[Optional()])
    submit = SubmitField('Gerar Relatório')
