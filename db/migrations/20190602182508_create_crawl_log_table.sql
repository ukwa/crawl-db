-- migrate:up
CREATE TABLE crawl_log (
  ssurt STRING,
  timestamp TIMESTAMP,
  url STRING,
  host STRING,
  domain STRING,
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
  ip INET,
  geocode STRING,
  virus STRING,
  crawl_name STRING,
  PRIMARY KEY (ssurt, timestamp)
);

-- Add an index to ensure we can filter by date range:
CREATE INDEX ON crawl_log (timestamp);

-- migrate:down
drop table crawl_log;
