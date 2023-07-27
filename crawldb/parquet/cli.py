import sys
import requests
import logging
import argparse
from crawldb.heritrix import CrawlLogLine
import pandas as pd
from fastparquet import write

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

def add_chunk(data: dict, append=True):
    columns = {}
    for key in data:
        if key in ['warc_offset', 'warc_length', 'wire_bytes', 'duration', 'content_length', 'status_code']:
            columns[key] = 'Int64'
    df = pd.DataFrame(data).astype(columns)
    write('outfile.parquet', df, append=append, compression='GZIP')
    #print(df.dtypes)
    #sys.exit(0)


def import_crawl_log(args, chunk_size=100_000):
    # Now read the file and push to the Crawl DB
    with open(args.filename, 'r') as f:
        count = 0
        chunk = {}
        append = False
        for line in f:
            c = CrawlLogLine(line)
            c_dict = c.to_dict()
            for key in c_dict:
                values = chunk.get(key, [])
                values.append(c_dict[key])
                chunk[key] = values
            count += 1
            if count%chunk_size == 0:
                add_chunk(chunk, append)
                chunk = {}
                logger.info(f"Done {count:,}...")
                if not append:
                    append = True
                #break
        if len(chunk) > 0:
            add_chunk(chunk)


def main(argv=None):
    parser = argparse.ArgumentParser('crawl-db')
    subparsers = parser.add_subparsers(help='crawl-db operation to perform', dest='command')

    # Import
    import_parser = subparsers.add_parser("import")
    import_parser.add_argument('filename', metavar='filename', help="Crawl log file to process")

    # Parse up:
    args = parser.parse_args()

    # Act:
    if args.command  == 'import':
        import_crawl_log(args)


if __name__ == "__main__":
    sys.exit(main())