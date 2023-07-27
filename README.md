# Crawl DB

A standalone database for crawl events.

## Overview

Take crawl events and turn them into Apache Parquet so they can be queried using tools like DuckDB, and so explored using things like Apache Superset.

Requires Python >= 3.8 to avoid fastparquet bug https://github.com/dask/fastparquet/issues/825

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

