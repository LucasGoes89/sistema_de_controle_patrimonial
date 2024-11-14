from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()

# Função para criar todos os modelos no banco de dados
def create_models():
    db.create_all()

# Definindo as classes diretamente, fora de qualquer função
class Usuario (UserMixin, db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    fullname = db.Column(db.String(128), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Funções adicionais para o Flask-Login
    def get_id(self):
        return self.id
    
class Bem(db.Model):
    __tablename__ = 'bem'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(128), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_aquisicao = db.Column(db.Date, nullable=False)
    valor = db.Column(db.Float, nullable=False)
    numero_serie = db.Column(db.String(64), unique=True, nullable=False)
    foto = db.Column(db.String(128), nullable=True)
    estado = db.Column(db.String(20), nullable=False, default="Disponível")
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship("Usuario", backref="bens")

class MovimentacaoBem(db.Model):
    __tablename__ = 'movimentacao_bem'
    id = db.Column(db.Integer, primary_key=True)
    bem_id = db.Column(db.Integer, db.ForeignKey("bem.id"), nullable=False)
    data = db.Column(db.DateTime, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    descricao = db.Column(db.Text)
    destino = db.Column(db.String(128))
    bem = db.relationship("Bem", backref="movimentacoes")

