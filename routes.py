from flask import render_template, redirect, url_for, flash, request, session, current_app, Flask
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, Bem, Usuario, MovimentacaoBem
from forms import RegistroForm, LoginForm, EditarBemForm, RegistrarEntradaForm, RegistrarSaidaForm, RegistrarTransferenciaForm, RelatoriosForm
from utils import registrar_movimentacao_bem
from werkzeug.utils import secure_filename
from datetime import datetime
from logging import getLogger, StreamHandler, Formatter
from datetime import datetime

import os
import logging
import pandas as pd
from flask import send_from_directory, current_app

# Definindo as extensões de arquivo permitidas
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads'


# Configurando logs
logger = getLogger("app")
handler = StreamHandler()
formatter = Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def register_routes(app):
    # Rota inicial para redirecionar ao login
    @app.route('/')
    def index():
        total_bens = Bem.query.count()
        disponiveis = Bem.query.filter_by(estado='Disponível').count()
        baixados = Bem.query.filter_by(estado='Baixado').count()
        
        return render_template('index.html', total_bens=total_bens, 
                            disponiveis=disponiveis, baixados=baixados)

    # Rota de logout
    @app.route("/logout")
    def logout():
        session.clear()
        flash("Logout efetuado com sucesso!")
        return redirect(url_for("auth.login"))

    # Rota para a página inicial (apenas para usuários logados)
    @app.route("/home")
    @login_required
    def home():
        bens = Bem.query.filter_by(usuario_id=current_user.id).all()
        total_bens = Bem.query.count()
        disponiveis = Bem.query.filter_by(estado='Disponível').count()
        baixados = Bem.query.filter_by(estado='Baixado').count()
        return render_template("index.html", bens=bens, total_bens=total_bens, 
                            disponiveis=disponiveis, baixados=baixados)

    # Rota para registrar um novo usuário
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            # Capturando os dados do formulário
            username = request.form['username']
            email = request.form['email']
            fullname = request.form['fullname']
            cpf = request.form['cpf']
            password = request.form['password']
            
            # Validando se o usuário já existe
            existing_user = Usuario.query.filter((Usuario.username == username) | (Usuario.email == email)).first()
            if existing_user:
                flash('Usuário ou e-mail já existente.')
                return redirect(url_for('register'))
            
            # Criptografando a senha
            hashed_password = generate_password_hash(password)

            # Criando um novo objeto de usuário
            novo_usuario = Usuario(username=username, email=email, fullname=fullname, cpf=cpf, password_hash=hashed_password)
            
            try:
                # Salvando no banco de dados
                db.session.add(novo_usuario)
                db.session.commit()
                flash('Usuário registrado com sucesso!')
                return redirect(url_for('index'))  # Redireciona ao login após o registro
            except Exception as e:
                logger.error(f'Erro ao registrar usuário: {e}')
                flash('Erro ao registrar usuário. Tente novamente.')

        return render_template('register.html')

    # Rota para cadastrar bens
    @app.route('/cadastrar_bens', methods=['GET', 'POST'])
    @login_required
    def cadastrar_bens():
        if request.method == 'POST':
            # Capturando os dados enviados pelo formulário
            nome = request.form.get('nome')
            descricao = request.form.get('descricao')
            data_aquisicao = request.form.get('data_aquisicao')
            valor = request.form.get('valor')
            numero_serie = request.form.get('numero_serie')

                # Verifica se uma foto foi enviada
            foto = request.files['foto']
            filename = None  # Define o filename como None caso a foto não seja enviada
            
            if foto and allowed_file(foto.filename):
                # Garante que o nome do arquivo é seguro
                filename = secure_filename(foto.filename)
                # Salva o arquivo na pasta de uploads
                foto.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


            # Validação simples (você pode adicionar mais validações se necessário)
            if not nome or not descricao or not data_aquisicao or not valor:
                flash('Por favor, preencha todos os campos obrigatórios.', 'danger')
                return redirect(url_for('cadastrar_bens'))

            try:
                # Convertendo a data e o valor para os tipos adequados
                data_aquisicao = datetime.strptime(data_aquisicao, '%Y-%m-%d').date()
                valor = float(valor)
                
                # Criando uma nova instância de Bem
                novo_bem = Bem(
                    nome=nome,
                    descricao=descricao,
                    data_aquisicao=data_aquisicao,
                    valor=valor,
                    numero_serie=numero_serie,
                    foto=filename,  # Armazena o nome da foto no banco de dados
                    usuario_id=current_user.id  # Ligando o bem ao usuário atual
                )

                # Adicionando o novo bem ao banco de dados
                db.session.add(novo_bem)
                db.session.commit()

                flash('Bem cadastrado com sucesso!', 'success')
                return redirect(url_for('listar_bens'))  # Redireciona para a lista de bens

            except ValueError as e:
                # Captura erros de conversão, como data ou número inválidos
                flash(f'Erro no cadastro: {str(e)}', 'danger')
                return redirect(url_for('cadastrar_bens'))

        # Se for uma requisição GET, exibe o formulário normalmente
        return render_template('cadastro_bens.html')

    # Rota para registrar saída de bem
    @app.route('/registrar_saida', methods=['GET', 'POST'])
    @login_required
    def registrar_saida_bem():
        form = RegistrarSaidaForm()
        if form.validate_on_submit():
            bem = Bem.query.filter_by(nome=form.nome_bem.data).first()
            if not bem:
                flash('Bem não encontrado.')
                return render_template('registrar_saida.html', form=form)

            bem.estado = form.estado.data
            registrar_movimentacao_bem(bem, datetime.now(), 'Saída', form.descricao.data)

            try:
                db.session.commit()
                flash('Saída de bem registrada com sucesso!')
                return redirect('/registrar-saida')
            except Exception as e:
                logger.error(f'Erro ao registrar saída de bem: {e}')
                flash('Erro ao registrar saída de bem. Tente novamente.')
                return render_template('registrar_saida.html', form=form)
        return render_template('registrar_saida.html', form=form)

    @app.route('/registrar_transferencia', methods=['GET', 'POST'])
    @login_required
    def registrar_transferencia():
        form = RegistrarTransferenciaForm()
        if form.validate_on_submit():
            bem = Bem.query.filter_by(nome=form.nome_bem.data).first()
            if not bem:
                flash('Bem não encontrado.')
                return render_template('registrar_transferencia.html', form=form)
            bem.estado = form.estado.data
            
            # Obter o destino da transferência
            destino = form.destino.data
            
            registrar_movimentacao_bem(bem, datetime.now(), 'Transferência', form.descricao.data, destino=destino)

            try:
                db.session.commit()
                flash('Transferência de bem registrada com sucesso!')
                return redirect('/registrar-transferencia')
            except Exception as e:
                logger.error(f'Erro ao registrar transferência de bem: {e}')
                flash('Erro ao registrar transferência de bem. Tente novamente.')
                return render_template('registrar_transferencia.html', form=form)
        return render_template('registrar_transferencia.html', form=form)

    @app.route('/bens', methods=['GET'])
    @login_required
    def listar_bens():   
        # Implementação da busca
        search_query = request.args.get('search', '')
        
        # Consulta base, filtrada pelo usuário logado
        bens_query = Bem.query.filter_by(usuario_id=current_user.id)

        if search_query:
            bens_query = bens_query.filter(Bem.nome.ilike(f'%{search_query}%'))
        
        bens = bens_query.all()
        return render_template('listar_bens.html', bens=bens, search_query=search_query)

    # Rota para visualizar os detalhes de um bem
    @app.route('/bem/<int:id>', methods=['GET'])
    @login_required
    def visualizar_bem(id):
        bem = Bem.query.get(id)

        if not bem or bem.usuario_id != current_user.id:
            flash('Bem não encontrado ou você não tem permissão para visualizá-lo.')
            return redirect('/home')

        return render_template('detalhes_bem.html', bem=bem)

    @app.route('/editar_bem/<int:bem_id>', methods=['GET', 'POST'])
    @login_required
    def editar_bem(bem_id):
        bem = Bem.query.get_or_404(bem_id)

        if request.method == 'POST':
            # Capturar os valores atuais para comparação
            valores_anteriores = {
                "nome": bem.nome,
                "descricao": bem.descricao,
                "data_aquisicao": bem.data_aquisicao,
                "valor": bem.valor,
                "numero_serie": bem.numero_serie,
                "estado": bem.estado,
            }

            # Atualizar os dados do bem com conversão correta
            bem.nome = request.form['nome']
            bem.descricao = request.form['descricao']
            
            # Converter a data do formulário para datetime.date
            data_aquisicao_str = request.form['data_aquisicao']
            bem.data_aquisicao = datetime.strptime(data_aquisicao_str, '%Y-%m-%d').date()

            bem.valor = float(request.form['valor'])  # Converter valor para float
            bem.numero_serie = request.form['numero_serie']
            bem.estado = request.form['estado']

            db.session.commit()

            # Registrar movimentações se houver alterações
            for campo, valor_antigo in valores_anteriores.items():
                valor_novo = getattr(bem, campo)
                if valor_antigo != valor_novo:
                    movimentacao = MovimentacaoBem(
                        bem_id=bem.id,
                        data=datetime.now(),
                        tipo='Edição',
                        descricao=f"Campo '{campo}' alterado de '{valor_antigo}' para '{valor_novo}'",
                        destino=current_user.fullname
                    )
                    db.session.add(movimentacao)

            db.session.commit()
            flash('Bem atualizado com sucesso!', 'success')
            return redirect(url_for('listar_bens'))

        return render_template('/editar_bem.html', bem=bem)

    @app.route('/confirmar_exclusao/<int:bem_id>', methods=['GET'])
    @login_required
    def confirmar_exclusao(bem_id):
        bem = Bem.query.get(bem_id)

        if not bem or bem.usuario_id != current_user.id:
            flash('Bem não encontrado ou você não tem permissão para excluí-lo.')
            return redirect('/bens')

        return render_template('confirmar_exclusao.html', bem=bem)

    @app.route('/excluir_bem/<int:bem_id>', methods=['POST'])
    @login_required
    def excluir_bem(bem_id):
        bem = Bem.query.get(bem_id)

        if bem and bem.usuario_id == current_user.id:
            try:
                # Se você estiver armazenando o caminho da imagem no banco de dados,
                # pode excluir o arquivo antes de deletar o bem
                if bem.foto:  # Supondo que você tenha um campo 'foto' no modelo 'Bem'
                    foto_path = os.path.join(app.config['UPLOAD_FOLDER'], bem.foto)
                    if os.path.exists(foto_path):
                        os.remove(foto_path)  # Remove a imagem do sistema de arquivos

                db.session.delete(bem)
                db.session.commit()
                flash('Bem excluído com sucesso!')
            except Exception as e:
                logger.error(f'Erro ao excluir o bem: {e}')
                flash('Erro ao excluir o bem. Tente novamente.')
        else:
            flash('Bem não encontrado ou você não tem permissão para excluí-lo.')

        return redirect('/bens')


    @app.route('/relatorios', methods=['GET', 'POST'])
    @login_required
    def gerar_relatorios():
        form = RelatoriosForm()

        if form.validate_on_submit():
            data_inicio = form.data_inicio.data
            data_fim = form.data_fim.data
            tipo_relatorio = form.tipo_relatorio.data

            # Consulta base, filtrada pelo usuário logado
            bens = Bem.query.filter(
                Bem.usuario_id == current_user.id,
                Bem.data_aquisicao >= data_inicio,
                Bem.data_aquisicao <= data_fim
            ).all()

            # Filtrar os bens por tipo de relatório
            if tipo_relatorio == 'Entrada':
                bens_filtrados = [bem for bem in bens if bem.estado == 'Disponível']
            elif tipo_relatorio == 'Saída':
                bens_filtrados = [bem for bem in bens if bem.estado != 'Disponível']
            elif tipo_relatorio == 'Transferência':
                bens_filtrados = [bem for bem in bens if bem.estado == 'Transferido']
            else:
                bens_filtrados = bens

            # Converter os dados para um DataFrame do Pandas
            dados = []
            for bem in bens_filtrados:
                dados.append({
                    'Nome': bem.nome,
                    'Descrição': bem.descricao,
                    'Data de Aquisição': bem.data_aquisicao.strftime('%d/%m/%Y'),
                    'Valor': bem.valor,
                    'Número de Série': bem.numero_serie,
                    'Estado': bem.estado
                })
            df = pd.DataFrame(dados)

            # Gerar o relatório em formato HTML
            html_table = df.to_html(index=False)

            # Renderizar a página com o relatório gerado
            return render_template('relatorios.html', form=form, dados_relatorio=html_table)

        return render_template('relatorios.html', form=form)

    @app.route('/controle_movimentacoes')
    @login_required
    def controle_movimentacoes():
        return render_template('controle_movimentacoes.html')
    
    @app.route('/detalhes_bem/<int:bem_id>')
    @login_required
    def detalhes_bem(bem_id):
        bem = Bem.query.get(bem_id)
        if bem and bem.usuario_id == current_user.id:
            return render_template('detalhes_bem.html', bem=bem)
        else:
            flash('Bem não encontrado ou você não tem permissão para visualizá-lo.')
            return redirect('/listar_bens')
        
    # Rota para servir arquivos do diretório de uploads
        
    @app.route('/uploads/<filename>')
    def uploads(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    @app.route('/disponivel')
    def bens_disponiveis():
        bens = Bem.query.filter_by(estado='Disponível').all()
        return render_template('relatorios.html', bens=bens, titulo='Relatório de Bens Disponíveis')

    @app.route('/baixado')
    def bens_baixados():
        bens = Bem.query.filter_by(estado='Baixado').all()
        return render_template('relatorios.html', bens=bens, titulo='Relatório de Bens Baixados')

    @app.route('/movimentacoes/<int:bem_id>')
    @login_required
    def movimentacoes(bem_id):
        bem = Bem.query.get_or_404(bem_id)
        return render_template('movimentacoes.html', bem=bem)