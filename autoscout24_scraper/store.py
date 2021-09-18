import json
from sqlite3 import Connection
from typing import Iterable

import pkg_resources

from .fetch import Auto


class Storage:
    def __init__(self, db_conn: Connection) -> None:
        self.db_conn = db_conn

        self._prepare_db()

    def store(self, data: Iterable[Auto]) -> None:
        with self.db_conn as c:
            c.executemany(
                '''INSERT INTO maker_model (
                    model,
                    version,
                    description,
                    price,
                    purchase_details,
                    mileage,
                    first_registration,
                    offer_type,
                    previous_owners,
                    transmission_type,
                    combined_consumption,
                    co2_emission,
                    unknown_details,
                    other
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                map(self._as_insert_params, data),
            )

    auto_fields = {
        'purchase_details': json.dumps,
        'unknown_details': json.dumps,
        'other': json.dumps,
    }

    def _as_insert_params(self, auto: Auto) -> None:
        def identity(x):
            return x

        return tuple(
            map(
                lambda x: self.auto_fields.get(x[0], identity)(x[1]),
                zip(Auto._fields, auto),
            )
        )

    def _prepare_db(self) -> None:
        with self.db_conn as c:
            try:
                c.execute('SELECT * FROM maker_model LIMIT 1')

            except Exception as e:
                schema = pkg_resources.resource_string(
                    __name__, 'sql/schema.sql'
                ).decode('utf-8')

                c.executescript(schema)
