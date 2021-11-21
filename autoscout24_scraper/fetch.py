from typing import Generator, NamedTuple, Optional
import logging
import re
from itertools import count
from decimal import Decimal
from urllib.parse import urlencode

from bs4.element import Tag
from mechanicalsoup import StatefulBrowser


logger = logging.getLogger(__name__)


class Auto(NamedTuple):
    model: str
    version: str
    description: str
    price: Optional[Decimal]
    purchase_details: list[str]
    mileage: Optional[str] = None
    first_registration: Optional[str] = None
    offer_type: Optional[str] = None
    previous_owners: Optional[str] = None
    transmission_type: Optional[str] = None
    combined_consumption: Optional[str] = None
    co2_emission: Optional[str] = None
    unknown_details: dict[str, str] = {}
    other: list[str] = []


class DataFetcher:
    price_rx = re.compile(r'€\s*([\d.,-]+)')
    price_footnote = 'Prezzo finale offerto al pubblico, comprensivo di IVA, non vincolato all’acquisto di un finanziamento, a permuta o rottamazione. Passaggio di proprietà e IPT esclusi.'

    def __init__(self, http_timeout: float = 20.0) -> None:
        self.br = StatefulBrowser()
        self.http_timeout = http_timeout

    def fetch_all(self, price_to: int, seats_from: int) -> Generator[Auto, None, None]:
        self.qs = {
            'sort': 'standard',
            'desc': 0,
            'fuel': 'E',
            'ustate': 'N,U',
            'size': '20',
            #'page': page,
            'cy': 'I',
            'priceto': price_to,
            'seatsfrom': seats_from,
            'atype': 'C',
        }

        for page in count(1):
            g = self.fetch(page)

            try:
                v = next(g)

                yield v

            except StopIteration:
                return

            yield from g

    def fetch(self, page: int) -> Generator[Auto, None, None]:
        self.qs['page'] = page

        # open raises IOError -> RequestException
        resp = self.br.open(
            f'https://www.autoscout24.it/lst?{urlencode(self.qs)}',
            timeout=self.http_timeout,
        )

        if resp.status_code != 200:
            logger.error('unexpected return code: page=%s, resp=%s', page, resp)

        page = self.br.page

        summary = page.find_all(
            'div', class_='cldt-summary-full-item-main'
        )  # cldt-summary-full-item

        logger.info('search results: page=%s, items=%s', page, len(summary))

        return map(self._parse_item, summary)

    def _parse_item(self, item: Tag) -> Auto:
        purchase_details = []
        price = None

        for x in item.find('span', class_='cldt-price').text.split('\n'):
            if not x:
                continue

            m = self.price_rx.search(x)

            if not m:
                purchase_details.append(x)

                continue

            if price is not None:
                logger.warning('found multiple prices: orig=%s, line=%s', price, x)

            price = Decimal(
                m.group(1).replace('.', '').replace(',', '.').replace('-', '0')
            )

        return Auto(
            model=self._optional_text(item, 'h2', 'cldt-summary-makemodel'),
            version=self._optional_text(item, 'h2', 'cldt-summary-version'),
            description=self._optional_text(item, 'h3', 'cldt-summary-subheadline'),
            price=price,
            purchase_details=purchase_details,
            **self._parse_details(item),
        )

    @staticmethod
    def _parse_details(item: Tag) -> dict[str, str]:
        details_list = item.find('ul')

        if details_list is None:
            logger.error('missing detail ul: item=%s', item)

            return {}

        details = {}

        for li in details_list.find_all('li'):
            txt = li.text.strip()
            data_type = li.attrs.get('data-type')

            if not data_type:
                details.setdefault('other', []).append(txt)

                continue

            field_name = data_type.replace('-', '_')

            if field_name not in Auto._fields:
                details.setdefault('unknown_details', {})[data_type] = txt

                continue

            details[field_name] = txt

        return details

    @staticmethod
    def _optional_text(item: Tag, tag_name: str, class_: str) -> Optional[str]:
        t = item.find(tag_name, class_=class_)

        if t is None:
            return None

        return t.text
