import sys
import duckdb

in_file = sys.argv[1]

def run_print_and_save(query, csv_file):
    q = duckdb.query(query)
    print(q)
    q.to_csv(csv_file)


print(duckdb.query(f"DESCRIBE SELECT * FROM '{in_file}'").df())

print(duckdb.query(f"SELECT COUNT(*) as total_records FROM '{in_file}'"))

#print(duckdb.query(f"SELECT * FROM '{in_file}' ORDER BY id ASC LIMIT 1"))
#print(duckdb.query(f"SELECT * FROM '{in_file}' ORDER BY id DESC LIMIT 1"))

# Scan for activity from a particular url_domain
#run_print_and_save(f"SELECT * FROM '{in_file}' WHERE url_domain == 'bbc.co.uk' LIMIT 10", "some_rows.csv")
run_print_and_save(f"SELECT * FROM '{in_file}' WHERE url LIKE '%service.gov.uk%' LIMIT 10", "some_rows.csv")
#run_print_and_save(f"SELECT * FROM '{in_file}' WHERE status_code == -5002 LIMIT 10", "some_rows.csv")

#run_print_and_save(f"SELECT url, start_time, STRPTIME(COALESCE(NULLIF(REGEXP_EXTRACT(annotations, '.*launchTimestamp:([0-9]+).*',1),''),'20300101000000'),'%Y%m%d%H%M%S') AS launch_time, (start_time - launch_time) AS delay, REGEXP_EXTRACT(annotations, '.*WebRenderStatus:([0-9]+).*',1) AS webrender_status_code, annotations FROM '{in_file}' WHERE status_code == -5002 AND delay IS NOT NULL ORDER BY delay DESC LIMIT 100", "some_rows.csv")
#print(duckdb.query(f"SELECT domain, status_code, COUNT(*) from '{in_file}' GROUP BY domain, status_code ORDER BY COUNT(*) DESC"))
#print(duckdb.query(f"SELECT domain, status_code, content_type, SUM(content_length), COUNT(*) from '{in_file}' WHERE domain == 'bbc.co.uk' GROUP BY domain, status_code, content_type ORDER BY COUNT(*) DESC"))

#print(duckdb.query(f"SELECT url_domain, status_code, COUNT(*) from '{in_file}' GROUP BY url_domain, status_code ORDER BY COUNT(*) DESC"))
#print(duckdb.query(f"SELECT url_domain, status_code, content_type, SUM(content_length), COUNT(*) from '{in_file}' GROUP BY url_domain, status_code, content_type ORDER BY COUNT(*) DESC"))
run_print_and_save(f"SELECT status_code, SUM(content_length) AS total_bytes, COUNT(*) AS total_records from '{in_file}' GROUP BY status_code ORDER BY COUNT(*) DESC", "status_codes.csv")

run_print_and_save(f"SELECT status_code, content_type, url_hostname, SUM(content_length) AS total_bytes, COUNT(*) AS total_records from '{in_file}' WHERE url LIKE '%gov.uk%' GROUP BY status_code, content_type, url_hostname ORDER BY COUNT(*) DESC", "gov_uk_summary.csv")
run_print_and_save(f"SELECT status_code, content_type, SUM(content_length) AS total_bytes, COUNT(*) AS total_records from '{in_file}' WHERE url LIKE '%service.gov.uk%' GROUP BY status_code, content_type ORDER BY COUNT(*) DESC", "gov_uk_assets_summary.csv")

#print(duckdb.query(f"SELECT url_domain, status_code, annotations, SUM(content_length), COUNT(*) from '{in_file}' WHERE url_domain == 'bbc.co.uk' GROUP BY url_domain, status_code, annotations  ORDER BY COUNT(*) DESC"))
#print(duckdb.query(f"SELECT url_domain, status_code, annotations, SUM(content_length), COUNT(*) from '{in_file}' WHERE url_domain == 'bbc.co.uk' GROUP BY url_domain, status_code, annotations  ORDER BY COUNT(*) DESC"))

#run_print_and_save(f"SELECT DATE_TRUNC('hour', STRPTIME(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')) as start_hour, COUNT(*) \
#FROM '{in_file}'  GROUP BY ALL ORDER BY start_hour ASC", "totals_by_hour.csv")

#run_print_and_save(f"SELECT DATE_TRUNC('hour', STRPTIME(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')) as start_hour, status_code, COUNT(*) \
#FROM '{in_file}' WHERE status_code == 200 OR status_code == -5003 OR status_code == -5002 \
#GROUP BY start_hour, status_code ORDER BY start_hour ASC, COUNT(*) DESC", "critical_status_codes_by_hour.csv")

#print(duckdb.query(f"COPY (SELECT DATE_TRUNC('hour', STRPTIME(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')) AS start_hour, url_domain, status_code, SUM(content_length) AS total_bytes, COUNT(*) \
#FROM '{in_file}' GROUP BY start_hour, url_domain, status_code ORDER BY start_hour ASC, status_code DESC) TO 'totals_by_hour_domain_status_code.csv'"))

#print(duckdb.query(f"SELECT ip, COUNT(*) from '{in_file}' WHERE ip IS NOT NULL GROUP BY ip ORDER BY COUNT(*) DESC"))
#print(duckdb.query(f"SELECT url_host, COUNT(*) from '{in_file}' WHERE status_code > 0 GROUP BY url_host ORDER BY COUNT(*) DESC"))
#print(duckdb.query(f"SELECT url_domain, COUNT(DISTINCT url_host) from '{in_file}' GROUP BY url_domain ORDER BY COUNT(DISTINCT url_host) DESC"))

#run_print_and_save(f"SELECT url, start_time, STRPTIME(COALESCE(NULLIF(REGEXP_EXTRACT(annotations, '.*launchTimestamp:([0-9]+).*',1),''),'20300101000000'),'%Y%m%d%H%M%S') AS launch_time, (start_time - launch_time) AS delay, REGEXP_EXTRACT(annotations, '.*WebRenderStatus:([0-9]+).*',1) AS webrender_status_code, annotations FROM '{in_file}' WHERE status_code == -5002 AND delay IS NOT NULL ORDER BY delay DESC LIMIT 100", "some_rows.csv")
run_print_and_save(f"SELECT url, tries, start_time, duration, launch_time, (start_time - launch_time) AS delay, webrender_status_code, annotations FROM '{in_file}' WHERE status_code == -5002 ORDER BY delay DESC LIMIT 100", "delayed_webrenders.csv")

