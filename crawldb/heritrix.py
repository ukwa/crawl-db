import re
import json
import urlcanon
import datetime
import tldextract

# Use a TLD extractor that down not download a new suffix list (uses embedded one)
custom_cache_extract = tldextract.TLDExtract(cache_dir=False)


class CrawlLogLine(object):
    """
    Parsers Heritrix3 format log files, including annotations and any additional extra JSON at the end of the line.
    """
    # Some regexes:
    re_ip = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    re_tries = re.compile('^\d+t$')
    re_dol = re.compile('^dol:\d+')  # Discarded out-links - make a total?

    def __init__(self, line, job_name=None, job_launch=None, log_filename=None):
        """
        Parse from a standard log-line.
        :param line:
        """
        # Store the line for reference
        self.line = line
        # Store the supplied metadata:
        self.job_name = job_name
        self.job_launch = job_launch
        self.log_filename = log_filename

        # Split the line up:
        (self.timestamp, self.status_code, self.content_length, self.url, self.hop_path, self.via,
            self.mime, self.thread, self.start_time_plus_duration, self.hash, self.source,
            self.annotation_string) = re.split(" +", line.strip(), maxsplit=11)
        # Account for any JSON 'extra info' ending, strip or split:
        if self.annotation_string.endswith(' {}'):
            self.annotation_string = self.annotation_string[:-3]
            self.extra_json = None
        elif ' {"' in self.annotation_string and self.annotation_string.endswith('}'):
            self.annotation_string, self.extra_json = re.split(re.escape(' {"'), self.annotation_string, maxsplit=1)
            self.extra_json = '{"%s' % self.extra_json
        # And split out the annotations:
        self.annotations = self.annotation_string.split(',')

        # Clean up:
        if self.content_length == "-":
            self.content_length = None
        else:
            self.content_length = int(self.content_length)
        if self.status_code:
            self.status_code = int(self.status_code)
        if self.source == '-':
            self.source = None

        # Parse URL:
        # FIXME Deal with dns:hostname URLs properly!
        parsed_url = urlcanon.parse_url(self.url)
        # Canonical form
        self.url_whatwg = urlcanon.whatwg(parsed_url)
        # and results:
        self.ssurt = parsed_url.ssurt().decode('utf-8')
        self.host = parsed_url.host.decode('utf-8')
        # Aggressively, canonicalised SURT:
        url_aggr = urlcanon.aggressive(parsed_url)
        self.surt = parsed_url.surt().decode('utf-8')

        # Host: DNS override
        if self.url.startswith("dns:"):
            self.host = self.url[4:]

        # Pull the registered domain:
        ext = custom_cache_extract(self.host)
        self.domain = ext.registered_domain
        self.public_suffix = ext.suffix

        # Default values
        self.ip = None
        self.tries = 1
        self.hop = ''
        self.launch_timestamp = None
        self.webrender_status_code = None

        # Interpret the timestamp
        self.timestamp_date =  datetime.datetime.strptime(self.timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')

        # Stats block
        self.stats = {
            'lines' : '', # This will count the lines under each split
            'status_code': self.status_code,
            'content_type': self.mime,
            'hop': self.hop_path[-1:],
            'sum:content_length': self.content_length,
            'host': self.host,
            'source': self.source
        }

        # Add in annotations:
        to_keep = []
        for annot in self.annotations:
            # Set a prefix based on what it is:
            prefix = ''
            if self.re_tries.match(annot):
                self.tries = int(annot[:-1])
            elif annot.startswith('ip:'):
                self.ip = annot[3:]
            elif annot.startswith('launchTimestamp:'):
                # launchTimestamp:20210903221019
                self.launch_timestamp = datetime.datetime.strptime(annot, "launchTimestamp:%Y%m%d%H%M%S")
            elif annot.startswith('WebRenderStatus:'):
                # WebRenderStatus:200
                self.webrender_status_code = int(annot[16:])
            else:
                to_keep.append(annot)
            # Only emit lines with annotations:
            if annot != "-":
                self.stats["%s%s" % (prefix, annot)] = ""
        # Avoid repeats, just keep the keepers:
        self.annotations = to_keep

        # Try to parse the extra JSON
        if self.extra_json:
            self.extra_json = json.loads(self.extra_json)
        else:
            self.extra_json = {}

    def to_dict(self):
        d = { 
            'id': '%s %s' % (self.surt, self.timestamp),
            'url': self.url,
            'url_hostname': self.host,
            'url_domain': self.domain,
            'url_public_suffix': self.public_suffix,
            'surt': self.surt,
            'ssurt': self.ssurt,
            'timestamp': self.timestamp_date,
            'status_code': self.status_code,
            'content_type': self.mime,
            'content_length': self.content_length,
            'hop_path': self.hop,
            'content_digest': self.hash,
            'ip': self.ip,
            'via': self.via,
            'seed': self.source,
            'tries': self.tries,
            'launch_time': self.launch_timestamp,
            'webrender_status_code': self.webrender_status_code,
            'annotations': self.annotations,
        }
        if '+' in self.start_time_plus_duration:
            st, dur = self.start_time_plus_duration.split('+')
            stdt = datetime.datetime.strptime(st, '%Y%m%d%H%M%S%f') 
            #d['start_time'] = '%sZ' % stdt.isoformat()
            d['start_time'] = stdt
            d['duration'] = int(dur)
        else:
            d['start_time'] = None
            d['duration'] = None

        if 'warcFilename' in self.extra_json:
            d['warc_type'] = 'response'
            d['warc_filename'] = self.extra_json['warcFilename']
            d['warc_offset'] = self.extra_json['warcFileOffset']
            d['warc_length'] = self.extra_json.get('warcFileRecordLength', None) # TODO How can this every be unset?
        else:
            d['warc_type'] = None
            d['warc_filename'] = None
            d['warc_offset'] = None
            d['warc_length'] = None

        if 'contentSize' in self.extra_json:
            d['wire_bytes'] = self.extra_json['contentSize']
        else:
            d['wire_bytes'] = None

        return d


    def stats(self):
        """
        This generates the stats that can be meaningfully aggregated over multiple log lines.
        i.e. fairly low-cardinality fields.

        :return:
        """
        return self.stats

    upsert_sql = """UPSERT INTO crawl_log (ssurt, timestamp, url, host, domain, content_type, content_length, content_digest, via, hop_path, status_code, ip, job_name, job_launch, log_filename ) VALUES %s"""

    def upsert_values(self):
        return (self.ssurt, self.timestamp, self.url, self.host, self.domain, self.mime, self.content_length, self.hash, self.via, self.hop_path, self.status_code, self.ip, self.job_name, self.job_launch, self.log_filename)
