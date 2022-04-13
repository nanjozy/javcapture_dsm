def connect(dsn: str = None, **kwargs):
    from psycopg2._psycopg import connection
    from psycopg2 import connect as get_connect
    from .function import safe_call
    if dsn is None:
        dsn = safe_call(get_dsn, **kwargs)
    timeout_params = {
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 5,
        "keepalives_count": 5,
    }
    conn: connection = get_connect(dsn=dsn, connect_timeout=60, **timeout_params)
    return conn


def get_dsn(dbname: str = None, user: str = None, password: str = None, host: str = None,
            port: int = None, keepass: str = None, **kwargs):
    from .libs import url_quote
    if keepass:
        from ..keepass import get_key
        config_obj = get_key(keepass)
        dbname = config_obj.get("dbname")
        user = config_obj.get("user")
        password = config_obj.get("password")
        host = config_obj.get("host")
        port = config_obj.get("port")
    dsn = 'postgresql://{user}:{password}@{host}:{port}/{dbname}'
    dsn = dsn.format(user=url_quote(user), password=url_quote(password), host=host, port=port,
                     dbname=url_quote(dbname))
    return dsn


def get_engine(**kwargs):
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool
    dsn = get_dsn(**kwargs)
    engine = create_engine(dsn, client_encoding='utf8', poolclass=QueuePool, pool_size=20, pool_pre_ping=True,
                           pool_recycle=1800, )
    return engine
