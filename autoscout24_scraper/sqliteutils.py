from sqlite3 import connect, Connection
from os.path import expanduser


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
