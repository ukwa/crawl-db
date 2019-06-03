-- migrate:up
CREATE TABLE crawl_log (
  url STRING,
  timestamp TIMESTAMP,
  content_type STRING,
  content_length INT,
  content_digest STRING,
  via STRING,
  hop_path STRING,
  hop STRING,
  source STRING,
  start_timestamp TIMESTAMP,
  duration INT,
  status_code INT,
  warc_filename STRING,
  warc_record_offset INT,
  warc_record_length INT,
  extra_info JSONB,
  host STRING,
  ip INET,
  geocode STRING,
  virus STRING,
  crawl_name STRING,
  PRIMARY KEY (url, timestamp)
);

-- Add an index to ensure we can filter by date range:
CREATE INDEX ON crawl_log (timestamp);
-- And for other reports:
CREATE INDEX ON crawl_log (content_type);
CREATE INDEX ON crawl_log (content_digest);
CREATE INDEX ON crawl_log (hop);
CREATE INDEX ON crawl_log (source);
CREATE INDEX ON crawl_log (status_code);
CREATE INDEX ON crawl_log (warc_filename);
CREATE INDEX ON crawl_log (host);
CREATE INDEX ON crawl_log (ip);
CREATE INDEX ON crawl_log (geocode);
CREATE INDEX ON crawl_log (virus);
CREATE INDEX ON crawl_log (crawl_name);

-- migrate:down
drop table crawl_log;
