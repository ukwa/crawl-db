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

        # Parse URL:
        # FIXME Deal with dns:hostnmae URLs properly!
        parsed_url = urlcanon.parse_url(self.url)
        # Canonicalise
        urlcanon.whatwg(parsed_url)

        # and results:
        self.ssurt = parsed_url.ssurt().decode('utf-8')
        self.host = parsed_url.host.decode('utf-8')
        # Pull the registered domain:
        ext = custom_cache_extract(self.host)
        self.domain = ext.registered_domain
        self.ip = None
        self.tries = None
        self.hop = ''
        # Host: DNS override
        if self.url.startswith("dns:"):
            self.host = self.url[4:]

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
        for annot in self.annotations:
            # Set a prefix based on what it is:
            prefix = ''
            if annot.startswith('tries:'):
                self.tries = int(annot[6:])
            elif annot.startswith('ip:'):
                self.ip = annot[3:]
            # Only emit lines with annotations:
            if annot != "-":
                self.stats["%s%s" % (prefix, annot)] = ""

        # Try to parse the extra JSON
        if self.extra_json:
            self.extra_json = json.loads(self.extra_json)

    def to_dict(self):
        d = { 
            'id': '%s/%s' % (self.timestamp, self.url),
            'url': self.url,
            'host': self.host,
            'domain': self.domain,
            'ip': self.ip,
            'timestamp': self.timestamp,
            'status_code': self.status_code,
            'content_type': self.mime,
            'content_length': self.content_length,
            'hop_path': self.hop,
            'annotations': self.annotations,
            'content_digest': self.hash,
            'via': self.via,
            'start_time_plus_duration': self.start_time_plus_duration,
            'seed': self.source
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
