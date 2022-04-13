# -*- coding: utf-8 -*-

def get_dsn(host: str = None, port: int = None, user: str = None, password: str = None,
            authdb: str = None, keepass: str = None, **kwargs) -> str:
    from urllib import parse
    if keepass:
        from ..keepass import get_key
        config_obj = get_key(keepass)
        host = config_obj.get("host")
        port = config_obj.get("port")
        user = config_obj.get("user")
        password = config_obj.get("password")
        authdb = config_obj.get("authdb")
    if authdb:
        authdb = parse.quote_plus(authdb)
    if user and password:
        user = parse.quote_plus(user)
        password = parse.quote_plus(password)
        url = 'mongodb://{user}:{password}@{host}:{port}/?authSource={authdb}&authMechanism=SCRAM-SHA-1'.format(
            user=user, password=password, host=host, port=port, authdb=authdb)
    else:
        url = 'mongodb://{host}:{port}/?authSource={authdb}'.format(host=host, port=port, authdb=authdb)
    return url


def mongo_client(**kwargs):
    from pymongo.mongo_client import MongoClient
    if "dsn" in kwargs.keys():
        dsn = kwargs.get("dsn")
    else:
        dsn = get_dsn(**kwargs)
    client: MongoClient = MongoClient(dsn, connect=False, retryWrites=False, maxPoolSize=5)
    return client
