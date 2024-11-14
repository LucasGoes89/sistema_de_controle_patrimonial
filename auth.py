from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required
from models import Usuario
from forms import RegistroForm, LoginForm

def create_auth_blueprint(app, db):
    auth_bp = Blueprint('auth', __name__)

    # Inicialize o Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Define o endpoint da rota de login
    login_manager.login_message = "Por favor, faça login para acessar esta página."

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    # Rota de registro
    @auth_bp.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistroForm()
        if form.validate_on_submit():
            username = form.username.data
            email = form.email.data
            password = form.password.data

            existing_user = Usuario.query.filter((Usuario.username == username) | (Usuario.email == email)).first()
            if existing_user:
                flash('Nome de usuário ou e-mail já cadastrados. Tente outro.')
                return redirect(url_for('auth.register'))

            hashed_password = generate_password_hash(password)

            try:
                new_user = Usuario(username=username, email=email, password_hash=hashed_password)
                db.session.add(new_user)
                db.session.commit()
                flash('Usuário registrado com sucesso!')
                return redirect(url_for('auth.login'))  # Atualizando para redirecionar corretamente
            except Exception as e:
                db.session.rollback()
                flash(f'Erro ao registrar usuário: {str(e)}. Tente novamente.')

        return render_template('register.html', form=form)

    # Rota de login
    @auth_bp.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # Pegar o nome de usuário e a senha do formulário
            username = request.form.get('username')
            password = request.form.get('password')

            # Verificar se o usuário existe
            user = Usuario.query.filter_by(username=username).first()

            # Verificar a senha e se o usuário é válido
            if user and check_password_hash(user.password_hash, password):
                login_user(user)  # Aqui o usuário é "salvo" na sessão
                return redirect(url_for('index'))  # Redirecionar para a página inicial
            else:
                flash('Nome de usuário ou senha incorretos')

        return render_template('login.html')

    # Rota de logout
    @auth_bp.route('/logout')
    @login_required
    def logout():
        logout_user()
        session.clear()
        flash('Logout realizado com sucesso!')
        return redirect(url_for('auth.login'))  # Atualizando para redirecionar corretamente

    return auth_bp
