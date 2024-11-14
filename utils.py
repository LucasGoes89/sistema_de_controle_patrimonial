from flask import current_app, flash
from models import db, MovimentacaoBem
from datetime import datetime
import logging

logger = logging.getLogger("app")

def registrar_movimentacao_bem(bem, data, tipo_movimentacao, descricao, destino=None):
    try:
        movimentacao = MovimentacaoBem(
            bem_id=bem.id, data=data, tipo=tipo_movimentacao, descricao=descricao, destino=destino
        )
        with current_app.app_context():
            db.session.add(movimentacao)
            db.session.commit()
        logger.info(f"Movimentação de bem registrada: {bem.nome} - {tipo_movimentacao}")
    except Exception as e:
        logger.error(f"Erro ao registrar movimentação de bem: {e}")
        flash("Erro ao registrar movimentação do bem. Tente novamente.")
