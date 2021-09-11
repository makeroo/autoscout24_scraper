from sqlite3 import Connection, OperationalError
from typing import Iterable

import pkg_resources

from .fetch import Auto


class Storage:
    def __init__(self, db_conn: Connection) -> None:
        self.db_conn = db_conn

        self._prepare_db()

    def store(self, data: Iterable[Auto]) -> None:
        pass

    def _prepare_db(self) -> None:
        with self.db_conn as c:
            try:
                c.execute('SELCT * FROM maker_model LIMIT 1')

            except OperationalError:
                schema = pkg_resources.resource_string(
                    __name__, 'sql/schema.sql'
                ).decode('utf-8')

                c.executescript(schema)
