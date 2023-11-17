import duckdb

in_file = 'outfile.parquet'
in_file = '/mnt/data/fc/crawl-db/npld-cp00004.parquet'

print(duckdb.query(f"DESCRIBE SELECT * FROM '{in_file}'"))
#print(duckdb.query(f"SELECT id,timestamp FROM '{in_file}' WHERE domain == 'bbc.co.uk' LIMIT 10"))
#print(duckdb.query(f"SELECT domain, status_code, COUNT(*) from '{in_file}' GROUP BY domain, status_code ORDER BY COUNT(*) DESC"))
#print(duckdb.query(f"SELECT domain, status_code, content_type, SUM(content_length), COUNT(*) from '{in_file}' WHERE domain == 'bbc.co.uk' GROUP BY domain, status_code, content_type ORDER BY COUNT(*) DESC"))
print(duckdb.query(f"SELECT DATE_TRUNC('hour', STRPTIME(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')) as start_hour, status_code, COUNT(*) \
FROM '{in_file}' WHERE status_code == 200 OR status_code == -5003 OR status_code == -5002 GROUP BY start_hour, status_code ORDER BY start_hour ASC, COUNT(*) DESC"))
#print(duckdb.query(f"SELECT ip, COUNT(*) from '{in_file}' WHERE ip IS NOT NULL GROUP BY ip ORDER BY COUNT(*) DESC"))
#print(duckdb.query(f"SELECT host, COUNT(*) from '{in_file}' WHERE status_code > 0 GROUP BY host ORDER BY COUNT(*) DESC"))
#print(duckdb.query(f"SELECT domain, COUNT(DISTINCT host) from '{in_file}' GROUP BY domain ORDER BY COUNT(DISTINCT host) DESC"))

