-- migrate:up

CREATE TABLE crawl_log (
  ssurt TEXT,
  timestamp TIMESTAMP,
  url TEXT,
  host TEXT,
  domain TEXT,
  content_type TEXT,
  content_length BIGINT,
  content_digest TEXT,
  via TEXT,
  hop_path TEXT,
  hop TEXT,
  source TEXT,
  start_timestamp TIMESTAMP,
  duration INT,
  status_code INT,
  warc_filename TEXT,
  warc_record_offset BIGINT,
  warc_record_length BIGINT,
  extra_info JSONB,
  ip INET,
  geocode TEXT,
  virus TEXT,
  job_name TEXT,
  job_launch TIMESTAMP,
  log_filename TEXT,
  PRIMARY KEY (ssurt, timestamp)
);
-- Add an index to ensure we can filter by date range:
CREATE INDEX ON crawl_log (timestamp);
-- Note that adding more indexes to this very detailed table is not recommended for large datasets.
-- Similarly, avoid replicating this table, to keep space utilisation reasonable:
ALTER TABLE crawl_log CONFIGURE ZONE USING num_replicas = 1;
-- TODO Requires an additional contraint to keep it on one large-capacity machine (more setup required for that).


-- Create an additional table to record every launch event.
-- (this helps rapidly locate crawl events in crawl_log)
CREATE TABLE crawl_launches (
  url TEXT,
  timestamp TIMESTAMP,
  job_name TEXT,
  stream TEXT,
  PRIMARY KEY (url, timestamp)
);
-- Add indexes to ensure we can filter by time, crawl_stream ('selective', 'domain', 'frequent') and job:
CREATE INDEX ON crawl_launches (timestamp);
CREATE INDEX ON crawl_launches (job_name);
CREATE INDEX ON crawl_launches (stream);


-- migrate:down

drop table crawl_log;

drop table crawl_launches;
