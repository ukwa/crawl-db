# Crawl DB

A standalone database for crawl events.

## Overview

Take crawl events and turn them into Apache Parquet so they can be queried using tools like DuckDB, and so explored using things like Apache Superset.

Requires Python >= 3.8 to avoid fastparquet bug https://github.com/dask/fastparquet/issues/825

At present, there is no MrJob/Map-Reduce version, but that could be added if needed.

## Example of use

During a crawl, we rapidly built up a lot of log activity. Some 37,357,947 log lines, in a 14.5GB file. This file was process like this:

python -m crawldb.parquet.cli import  crawl.log.cp00004-20231116123457 crawl-log-cp00004.parquet

This took a while, about an hour, but created a queryable file only 2.8GB in size.

Using the example queries (see `duckdb-query.py` for details), we could query this file very quickly, with even fairly intensive aggregation queries only requiring a second or so to run. Some simple examples are:


### Total records

```
SELECT COUNT(*) FROM 'crawl-log-cp00004.parquet';

┌──────────────┐
│ count_star() │
│    int64     │
├──────────────┤
│     37357947 │
└──────────────┘
```


### Breakdown by status codes

```
SELECT status_code, SUM(content_length) AS total_bytes, COUNT(*) AS total_records from 'crawl-log-cp00004.parquet' GROUP BY status_code ORDER BY COUNT(*) DESC;

┌─────────────┬──────────────┬───────────────┐
│ status_code │ total_bytes  │ total_records │
│    int64    │    int128    │     int64     │
├─────────────┼──────────────┼───────────────┤
│       -5003 │         NULL │      30199915 │
│         200 │ 561472969271 │       4868164 │
│       -9998 │         NULL │        613207 │
│         301 │    336555824 │        574581 │
│         302 │    459076182 │        344545 │
│         403 │    977360013 │        228733 │
│         404 │   8837109684 │        193986 │
│          -6 │         NULL │         87998 │
│         307 │       668014 │         66263 │
│         503 │    188275757 │         44856 │
│          ·  │           ·  │             · │
│          ·  │           ·  │             · │
│          ·  │           ·  │             · │
│         415 │          336 │             3 │
│         421 │          513 │             3 │
│         402 │        12790 │             2 │
│         417 │            0 │             2 │
│         299 │       314915 │             2 │
│         203 │        14252 │             1 │
│         524 │         7222 │             1 │
│         999 │         1530 │             1 │
│         408 │        12448 │             1 │
│          -5 │         NULL │             1 │
├─────────────┴──────────────┴───────────────┤
│ 63 rows (20 shown)               3 columns │
└────────────────────────────────────────────┘
```


## Previous Designs

There have been many different versions and re-designs of this approach over the years. e.g. Monitrix on Cassandra, then on ElasticSearch. And then directly using Solr, and later CockroachDB.  All have been problematic because of the resources required to run these tools at the scale of UK domain crawls.

This latest design avoids a lot of that complexity by instead targeting the generation of static files in the Parquet format. This provides an efficient way to store data, while not requiring complex additional infrastructure.  For modest sizes, we can just store them on local disk. For larger collections, we can store them on HDFS.

The first experiment with this showed that we could take an 11GB crawl log containing over 22 million crawl events, and store it in Parquet using GZIP compression in just 3GB (136 bytes per line). This format is also much easier to work with, and on a decent machine with SSD disks, could be use to run large aggregated queries in less than a second. See `duckdb-query.py` for examples.

