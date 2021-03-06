def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-d', '--database', default='~/.a24scraper.db')
    parser.add_argument('--http-timeout', type=float, default=20.0)
    parser.add_argument('--price-to', type=int, default=20000)
    parser.add_argument('--seats-from', type=int, default=5)

    args = parser.parse_args()

    import logging

    logging.basicConfig(
        level=max(logging.DEBUG, logging.WARNING - args.verbose * 10),
    )

    from .sqliteutils import create_connection

    db_conn = create_connection(args.database)

    from .store import Storage

    storage = Storage(db_conn)

    from .fetch import DataFetcher

    fetcher = DataFetcher(args.http_timeout)

    storage.store(
        fetcher.fetch_all(
            price_to=args.price_to,
            seats_from=args.seats_from,
        )
    )

    db_conn.close()


if __name__ == '__main__':
    main()
