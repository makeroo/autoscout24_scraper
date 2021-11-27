import json
from sqlite3 import Connection, Cursor
from typing import Iterable
from datetime import datetime

import pkg_resources

from .fetch import Auto


class Storage:
    def __init__(self, db_conn: Connection) -> None:
        self.db_conn = db_conn

        self._prepare_db()

    def _maker_model(self, c, model: str, version: str) -> int:
        args = (model, version)

        while True:
            c.execute('SELECT id FROM maker_model WHERE model=? AND version=?', args)

            try:
                return c.fetchone()[0]

            except Exception as e:
                pass

            try:
                c.execute(
                    'INSERT INTO maker_model (model, version) VALUES (?, ?)', args
                )

            except Exception as e:
                pass

    def store(self, data: Iterable[Auto]) -> None:
        with self.db_conn as c:
            cur = c.cursor()

            for auto in data:
                self._insert_auto(cur, auto)

    def _ad_id(self, c: Cursor, auto: Auto) -> int:
        c.execute('SELECT id FROM ad WHERE ad_id=?', (auto.guid,))

        r = c.fetchone()

        if r is not None:
            return r[0]

        model_id = self._model_id(c, auto)

        c.execute('INSERT INTO ad(model_id, ad_id) VALUES(?, ?)', (model_id, auto.guid))

        return c.lastrowid

    def _model_id(self, c: Cursor, auto: Auto) -> int:
        model_attrs = (auto.model, auto.version)

        c.execute('SELECT id FROM maker_model WHERE model=? AND version=?', model_attrs)

        r = c.fetchone()

        if r is not None:
            return r[0]

        c.execute(
            'INSERT INTO maker_model(model, version) VALUES (?, ?)',
            (auto.model or '', auto.version or ''),
        )

        return c.lastrowid

    def _insert_auto(self, c: Cursor, auto: Auto) -> None:
        ad_id = self._ad_id(c, auto)

        c.execute(
            '''
 SELECT description, price, purchase_details, mileage, first_registration, offer_type,
        previous_owners, transmission_type, combined_consumption, co2_emission,
        unknown_details, other
   FROM ad_update
  WHERE ad_id=?
ORDER BY first_fetch DESC
   LIMIT 1''',
            (ad_id,),
        )

        r = c.fetchone()

        now = datetime.utcnow()

        record = (
            ad_id,
            now,
            now,
            auto.description,
            auto.price,
            json.dumps(auto.purchase_details),
            auto.mileage,
            auto.first_registration,
            auto.offer_type,
            auto.previous_owners,
            auto.transmission_type,
            auto.combined_consumption,
            auto.co2_emission,
            json.dumps(auto.unknown_details),
            json.dumps(auto.other),
        )

        if r is not None and r == record[3:]:
            c.execute('UPDATE ad_update SET last_fetch=? WHERE ad_id=?', (now, ad_id))

            return

        c.execute(
            '''INSERT INTO ad_update (
                ad_id,
                first_fetch,
                last_fetch,
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            record,
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
