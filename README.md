# Crawl DB

n.b. requires Python >= 3.8 to avoid fastparquet bug https://github.com/dask/fastparquet/issues/825

A standalone database for crawl events.

Any PostgreSQL-compliant database can be used.



    docker run -ti cockroachdb/cockroach:v19.1.1 sql --insecure --url postgresql://root@192.168.45.21:26257/
