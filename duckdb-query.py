import duckdb

in_file = 'outfile.parquet'

print(duckdb.query(f"DESCRIBE SELECT * FROM '{in_file}'"))
#print(duckdb.query(f"SELECT * FROM '{in_file}' WHERE domain == 'gavabiz.co.uk' LIMIT 10"))
print(duckdb.query(f"SELECT domain, status_code, COUNT(*) from '{in_file}' GROUP BY domain, status_code ORDER BY COUNT(*) DESC"))
print(duckdb.query(f"SELECT ip, COUNT(*) from '{in_file}' WHERE ip IS NOT NULL GROUP BY ip ORDER BY COUNT(*) DESC"))
print(duckdb.query(f"SELECT host, COUNT(*) from '{in_file}' WHERE status_code > 0 GROUP BY host ORDER BY COUNT(*) DESC"))
print(duckdb.query(f"SELECT domain, COUNT(DISTINCT host) from '{in_file}' GROUP BY domain ORDER BY COUNT(DISTINCT host) DESC"))

