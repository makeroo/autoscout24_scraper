from sqlite3 import connect, Connection, register_adapter, register_converter
from os.path import expanduser
from decimal import Decimal


def adapt_decimal(d: Decimal) -> str:
    return str(d)


def convert_decimal(s: str) -> Decimal:
    return Decimal(s)


register_adapter(Decimal, adapt_decimal)

register_converter("decimal", convert_decimal)


def create_connection(uri: str) -> Connection:
    """
    Support unix-style ~ in path.
    Example: ~/pippo -> /home/someone/pippo
    Example: file:~/pippo -> same as above
    """

    if uri.startswith('file:'):
        uri = uri[5:]

    path = expanduser(uri)

    return connect(path)
