import os
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

def add_chunk(data: dict, outfile, append=True):
    columns = {}
    for key in data:
        if key in ['warc_offset', 'warc_length', 'wire_bytes', 'duration', 'content_length', 'status_code']:
            columns[key] = 'Int64'
    df = pd.DataFrame(data).astype(columns)
    write(outfile, df, append=append, compression='GZIP')
    #print(df.dtypes)
    #sys.exit(0)


def import_crawl_log(args, chunk_size=100_000):
    # Now read the file and push to the Crawl DB
    with open(args.filename, 'r') as f:
        count = 0
        chunk = {}
        append = False
        for line in f:
            try:
                c = CrawlLogLine(line)
            except Exception as e:
                logger.error(f"Could not parse line: {line}")
                raise e
            c_dict = c.to_dict()
            for key in c_dict:
                values = chunk.get(key, [])
                values.append(c_dict[key])
                chunk[key] = values
            count += 1
            if count%chunk_size == 0:
                add_chunk(chunk, args.output, append)
                chunk = {}
                logger.info(f"Written {count:,} records...")
                if not append:
                    append = True
                #break
        if len(chunk) > 0:
            add_chunk(chunk, args.output)


def main(argv=None):
    parser = argparse.ArgumentParser('crawl-db')
    subparsers = parser.add_subparsers(help='crawl-db operation to perform', dest='command')

    # Import
    import_parser = subparsers.add_parser("import")
    default_chunk_size = 100_000
    import_parser.add_argument('--chunk-size', type=int, default=default_chunk_size, help=f"number of records to put into each chunk appended to the output file (default: {default_chunk_size:,})")
    import_parser.add_argument('filename', metavar='filename', help="crawl log file to process")
    import_parser.add_argument('output', metavar='output', help="parquet file to create")

    # Parse up:
    args = parser.parse_args()

    # Act:
    if args.command  == 'import':
        import_crawl_log(args)


if __name__ == "__main__":
    sys.exit(main())
