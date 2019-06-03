import re
from urllib.parse import urlparse


class CrawlLogLine(object):
    """
    Parsers Heritrix3 format log files, including annotations and any additional extra JSON at the end of the line.
    """
    # Some regexes:
    re_ip = re.compile('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
    re_tries = re.compile('^\d+t$')
    re_dol = re.compile('^dol:\d+')  # Discarded out-links - make a total?

    def __init__(self, line):
        """
        Parse from a standard log-line.
        :param line:
        """
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

        # and results:
        self.ip = None
        self.tries = None
        self.hop = ''
        # Host
        if self.url.startswith("dns:"):
            self.host = self.url[4:]
        else:
            self.host = urlparse(self.url).hostname

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
            if self.re_tries.match(annot):
                prefix = 'tries:'
                self.tries = annot
            elif self.re_ip.match(annot):
                prefix = "ip:"
                self.ip = annot
            # Only emit lines with annotations:
            if annot != "-":
                self.stats["%s%s" % (prefix, annot)] = ""


    def stats(self):
        """
        This generates the stats that can be meaningfully aggregated over multiple log lines.
        i.e. fairly low-cardinality fields.

        :return:
        """
        return self.stats
