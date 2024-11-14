class Config:
    # Configurações básicas
    SECRET_KEY = "uma-chave-secreta"
    DEBUG = True

    # Configurações do banco de dados (SQLite)
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
