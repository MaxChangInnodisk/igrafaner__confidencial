from collections import namedtuple


class SqlParams:

    def __init__(self,
                 host: str,
                 port: str,
                 user: str,
                 password: str,
                 database: str) -> None:
        self.host: str = host
        self.port: str = port
        self.user: str = user
        self.password: str = password
        self.database: str = database


MySQL = SqlParams(
    host="127.0.0.1",
    port="3306",
    user="",
    password="",
    database="grafana"
)
