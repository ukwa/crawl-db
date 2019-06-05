import sys
import logging
import argparse
import psycopg2
from psycopg2.extras import execute_values
from crawldb.heritrix import CrawlLogLine

# Set up a logging handler:
handler = logging.StreamHandler()
# handler = logging.StreamHandler(sys.stdout) # To use stdout rather than the default stderr
formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(filename)s.%(funcName)s: %(message)s")
handler.setFormatter(formatter)

# Attach to root logger
logging.root.addHandler(handler)

# Set default logging output for all modules.
logging.root.setLevel(logging.WARNING)

# Set logging for this module and keep the reference handy:
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def value_generator(f):
    for line in f:
        c = CrawlLogLine(line)
        yield c.upsert_values()


def import_crawl_log(args, cur):
    # Now read the file and push to the Crawl DB
    # : url, timestamp, content_type, content_length, content_digest, via, hop_path, hop, source, start_timestamp, duration, status_code, warc_filename, warc_record_offset, warc_record_length, extra_info, host, ip, geocode, virus, crawl_name)
    with open(args.filename, 'r') as f:
        # Use batch insertion helper:
        execute_values(
            cur,
            CrawlLogLine.upsert_sql,
            value_generator(f),
            page_size=1000
        )


def query(args, cur):
    # Example query:
    cur.execute("""
        SELECT host, date_trunc('hour', timestamp), SUM(content_length) 
        FROM crawl_log 
        WHERE timestamp > '2016-03-31 15:00:00' AND timestamp < '2016-03-31 16:00:00' 
        GROUP BY host, date_trunc('hour', timestamp)
        """)
    #rows = cur.fetchall()
    # Returns:
    #for row in rows:
    # Returns (streaming style):
    for row in cur:
        print([str(cell) for cell in row])


def main(argv=None):
    parser = argparse.ArgumentParser('crawl-db')
    subparsers = parser.add_subparsers(help='crawl-db operation to perform', dest='command')
    # Common args:
    parser.add_argument('-d', '--database-uri', dest='database_uri', type=str, default="postgres://root@crdb:26257/defaultdb?sslmode=disable",
                        help="PostgreSQL database to use [default: %(default)s]")

    # Import
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument('filename', metavar='filename', help="Crawl log file to process")

    # Query
    query_parser = subparsers.add_parser("query")

    # Parse up:
    args = parser.parse_args()

    # Connect to the "bank" database.
    conn = psycopg2.connect(
        database='defaultdb',
        user='root',
        sslmode='disable',
        port=26257,
        host='localhost',
    )

    # Make each statement commit immediately.
    conn.set_session(autocommit=True)

    # Open a cursor to perform database operations.
    cur = conn.cursor()

    # Act:
    if args.command  == 'import':
        import_crawl_log(args,cur)
    elif args.command == 'query':
        query(args,cur)


    # Close the database connection.
    cur.close()
    conn.close()

if __name__ == "__main__":
    sys.exit(main())
