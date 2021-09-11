def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-d', '--database', default='~/.a24scraper.db')

    args = parser.parse_args()

    import logging

    logging.basicConfig(
        level=max(logging.DEBUG, logging.WARNING - args.verbose * 10),
    )

    from sqliteutils import create_connection

    db_conn = create_connection(args.database)
    pass


if __name__ == '__main__':
    main()
