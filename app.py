import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from auth import create_auth_blueprint
from routes import register_routes  # Importe suas rotas aqui
from models import create_models, Usuario

app = Flask(__name__)
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Rota para redirecionamento ao login
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
# app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Verifica se o diretório 'uploads' existe, senão cria
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

db = SQLAlchemy(app)

# Registre o blueprint de autenticação
auth_bp = create_auth_blueprint(app, db)
app.register_blueprint(auth_bp, url_prefix='/auth')  # Adiciona o prefixo /auth

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Registre suas rotas principais
register_routes(app)

# Criação das tabelas no banco de dados
with app.app_context():
    create_models()  # Isso criará todas as tabelas se ainda não existirem

if __name__ == '__main__':
    app.run(debug=True)