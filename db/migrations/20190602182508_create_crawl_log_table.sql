-- migrate:up
CREATE TABLE crawl_log (
  ssurt TEXT,
  timestamp TIMESTAMP,
  event_id BIGINT, -- This is a simple numeric ID used to ensure events that happen at exactly the same time can be distinguished
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
  PRIMARY KEY (ssurt, timestamp, event_id)
);
-- Add an index to ensure we can filter by date range:
CREATE INDEX ON crawl_log (timestamp);

-- Create an additional table to record every launch event:
CREATE TABLE crawl_launches (
  url TEXT,
  timestamp TIMESTAMP,
  job_name TEXT,
  PRIMARY KEY (url, timestamp)
);

-- Create a table to store information about the WARC (and log?) files
--- CockroachDB does not support ENUM yet, so commented out:
--- CREATE TYPE file_type AS ENUM ('warc', 'invalid-warc', 'viral', 'crawl-log','log', 'dlx', 'cdx', 'unknown');
--- CREATE TYPE crawl_stream AS ENUM ('selective', 'domain', 'frequent');
--- CREATE TYPE crawl_terms AS ENUM ('npld', 'by-permission')
CREATE TABLE crawl_files (
  filename TEXT,
  crawl_job_name TEXT,
  crawl_job_launch TIMESTAMP,
  extension TEXT,
  digest TEXT,
  type TEXT, --- file_type,        -- e.g. 'warc'
  storage_uri TEXT ARRAY,          -- List of URIs indicating where this file is stored
  created_at TIMESTAMP,
  stream TEXT, --- crawl_stream,
  terms TEXT, --- crawl_terms,
  ppid TEXT ARRAY,                 -- Primary Permanent IDentifier for this resource (e.g. an ARK)
  PRIMARY KEY (filename, crawl_job_name, crawl_job_launch)
);

-- migrate:down
drop table crawl_log;

drop table crawl_launches;

drop table crawl_files;