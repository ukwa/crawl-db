# Crawl DB

A standalone database for crawl events.

## Overview

Take crawl events and turn them into Apache Parquet so they can be queried using tools like DuckDB, and so explored using things like Apache Superset.

Requires Python >= 3.8 to avoid fastparquet bug https://github.com/dask/fastparquet/issues/825

## Example of use

14.5G  100 14.5G    0     0  48.1M      0  0:05:08  0:05:08 --:--:-- 52.2M
[ec2-user@fc crawl-db]$ wc crawl.log.cp00004 
   37357947   635085091 15578444671 crawl.log.cp00004


(.venv) [ec2-user@fc crawl-db]$  head -1 /mnt/data/fc/crawl-db/crawl.log.cp00004 
2023-11-15T17:13:05.828Z -5003          - https://cdn.mos.cms.futurecdn.net/EaNfygyiNnxXmUAXnpcojG-768-80.jpeg LE https://www.wallpaper.com/fashion-beauty/sacai-mercedes-benz-amg-collaboration unknown #070 - - tid:94192:https://www.wallpaper.com/ Q:serverMaxSuccessKb {"scopeDecision":"ACCEPT by rule #2 MatchesRegexDecideRule"}
(.venv) [ec2-user@fc crawl-db]$  tail -1 /mnt/data/fc/crawl-db/crawl.log.cp00004 
2023-11-16T12:36:14.536Z   200     357908 https://www.thegazette.co.uk/sitemap-201709-1.xml.gz II https://www.thegazette.co.uk/sitemap.xml application/xml #137 20231116115454719+406 sha1:YUPZK5EJ7WRFWRRLD3CMGHH7ZQW3NDX7 tid:37575:https://www.thegazette.co.uk/ isSitemap,launchTimestamp:20231115090324,err=java.lang.NullPointerException,dol:50002,ip:18.165.201.84 {"contentSize":358576,"warcFilename":"BL-NPLD-20231116115015552-01164-44~npld-heritrix3-worker-1~8443.warc.gz","warcFileOffset":220898170,"scopeDecision":"ACCEPT by rule #1 WatchedFileSurtPrefixedDecideRule","warcFileRecordLength":460354}   

 1098  2023-11-16:13:05:01  python -m crawldb.parquet.cli import  /mnt/data/fc/heritrix/output/frequent-npld/20231115123452/logs/crawl.log.cp00004-20231116123457 /mnt/data/fc/crawl-db/npld-cp00004.parquet

 -rw-r--r--. 1 ec2-user ec2-user 2.8G Nov 16 15:33 npld-cp00004.parquet

┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│     37357947 │
└──────────────┘


┌──────────────────────┬──────────────────────┬──────────────────────┬───────────────┬─────────┬───┬───────────────┬─────────────┬─────────────┬────────────┐
│          id          │         url          │         host         │    domain     │   ip    │ … │ warc_filename │ warc_offset │ warc_length │ wire_bytes │
│       varchar        │       varchar        │       varchar        │    varchar    │ varchar │   │    varchar    │    int64    │    int64    │   int64    │
├──────────────────────┼──────────────────────┼──────────────────────┼───────────────┼─────────┼───┼───────────────┼─────────────┼─────────────┼────────────┤
│ 2023-11-15T17:13:0…  │ https://cdn.mos.cm…  │ cdn.mos.cms.future…  │ futurecdn.net │ NULL    │ … │ NULL          │        NULL │        NULL │       NULL │
├──────────────────────┴──────────────────────┴──────────────────────┴───────────────┴─────────┴───┴───────────────┴─────────────┴─────────────┴────────────┤
│ 1 rows                                                                                                                               22 columns (9 shown) │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┬──────────────────────┬──────────────────────┬──────────────────┬───┬──────────────────────┬─────────────┬─────────────┬────────────┐
│          id          │         url          │         host         │      domain      │ … │    warc_filename     │ warc_offset │ warc_length │ wire_bytes │
│       varchar        │       varchar        │       varchar        │     varchar      │   │       varchar        │    int64    │    int64    │   int64    │
├──────────────────────┼──────────────────────┼──────────────────────┼──────────────────┼───┼──────────────────────┼─────────────┼─────────────┼────────────┤
│ 2023-11-16T12:36:1…  │ https://www.thegaz…  │ www.thegazette.co.uk │ thegazette.co.uk │ … │ BL-NPLD-2023111611…  │   220898170 │      460354 │     358576 │
├──────────────────────┴──────────────────────┴──────────────────────┴──────────────────┴───┴──────────────────────┴─────────────┴─────────────┴────────────┤
│ 1 rows                                                                                                                               22 columns (8 shown) │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘



 

## To Do

- Make some DC2023 data accessible via Apache Superset to explore if we need more fields.
- Match the Common Crawl parquet schema if possible.
- Remove Solr/CRDB code and simplify the dependencies as much as possible.
- Consider whether this can be integrated with the Kafka streams, so we can have recent data in a queriable form that is easier to manage than the ELK stack (which can't cope with domain crawl scale)
- Make a Map-Reduce version so we can generate parquet from crawl log lines efficiently.
- Allow integration of richer data from WARCs, e.g. a `webarchive-discovery` tool-chain than can generate compatible Parquet files.

## Previous Designs

There have been many different versions and re-designs of this approach over the years. e.g. Monitrix on Cassandra, then on ElasticSearch. And then directly using Solr, and later CockroachDB.  All have been problematic because of the resources required to run these tools at the scale of UK domain crawls.

This latest design avoids a lot of that complexity by instead targeting the generation of static files in the Parquet format. This provides an efficient way to store data, while not requiring complex additional infrastructure.  For modest sizes, we can just store them on local disk. For larger collections, we can store them on HDFS.

The first experiment with this showed that we could take an 11GB crawl log containing over 22 million crawl events, and store it in Parquet using GZIP compression in just 3GB (136 bytes per line). This format is also much easier to work with, and on a decent machine with SSD disks, could be use to run large aggregated queries in less than a second. See `duckdb-query.py` for examples.

