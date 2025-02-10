class Config:
    SECRET_KEY = 'sua-chave-secreta-muito-segura'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None  # Sem limite de tempo para o token CSRF
    WTF_CSRF_ENABLED = True
    WTF_CSRF_HEADERS = ['X-CSRF-TOKEN']
    WTF_CSRF_CHECK_DEFAULT = False
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 86400
