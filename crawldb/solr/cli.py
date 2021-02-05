import sys
import requests
import logging
import argparse
from crawldb.heritrix import CrawlLogLine
from kevals.solr import SolrKevalsDB

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
    count = 0
    for line in f:
        c = CrawlLogLine(line)
        yield c.to_dict()
        count += 1
        if count%1000 == 0:
            logger.info("Sent %s..." % count )

def import_crawl_log(args, skvdb):
    # Now read the file and push to the Crawl DB
    with open(args.filename, 'r') as f:
        skvdb.import_items_from(value_generator(f))

def query(args, skvdb):
    # Example query:
    #cur.execute("""SELECT COUNT(*) FROM crawl_log;""");
    cur.execute("""SELECT * FROM crawl_log WHERE hop_path = '-' AND ( status_code < 200 OR status_code > 399)""")
    # Returns (streaming style):
    for row in cur:
        print([str(cell) for cell in row])


def main(argv=None):
    parser = argparse.ArgumentParser('crawl-db')
    subparsers = parser.add_subparsers(help='crawl-db operation to perform', dest='command')
    # Common args:
    parser.add_argument('-S', '--solr-url', dest='solr_url', type=str, default="http://localhost:8913/solr/crawl_log_fc",
                        help="URL of Solr Collection to use [default: %(default)s]")

    # Import
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument('filename', metavar='filename', help="Crawl log file to process")

    # Query
    query_parser = subparsers.add_parser("query")

    # Parse up:
    args = parser.parse_args()

    # Setup DB:
    skvdb = SolrKevalsDB(args.solr_url)

    # Act:
    if args.command  == 'import':
        import_crawl_log(args, skvdb)
    elif args.command == 'query':
        query(args, skvdb)


if __name__ == "__main__":
    sys.exit(main())
