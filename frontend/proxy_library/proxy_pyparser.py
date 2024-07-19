# -*- coding: utf-8 -
#
# This file is part of http-parser released under the MIT license.
# See the NOTICE for more information.

import os
import re
import sys

from typing import Dict

if sys.version_info >= (3,):
    import urllib.parse as urlparse
else:
    import urlparse

import zlib


import sys
try:
    # Python 3.3+
    from collections.abc import MutableMapping
except ImportError:
    from collections import MutableMapping


if sys.version_info[0] >= 3:
    from urllib.parse import unquote
    def b(s):
        return s.encode("latin-1")

    def bytes_to_str(b):
        return str(b, 'latin1')

    string_types = str,

    import io
    StringIO = io.StringIO

    MAXSIZE = sys.maxsize

else:
    from urllib import unquote
    def b(s):
        return s

    def bytes_to_str(s):
        return s

    string_types = basestring,

    try:
        import cStringIO
        StringIO = BytesIO = cStringIO.StringIO
    except ImportError:
        import StringIO
        StringIO = BytesIO = StringIO.StringIO

    # It's possible to have sizeof(long) != sizeof(Py_ssize_t).
    class X(object):
        def __len__(self):
            return 1 << 31
    try:
        len(X())
    except OverflowError:
        # 32-bit
        MAXSIZE = int((1 << 31) - 1)
    else:
        # 64-bit
        MAXSIZE = int((1 << 63) - 1)
    del X

class IOrderedDict(dict, MutableMapping):
    'Dictionary that remembers insertion order with insensitive key'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, and get.
    # The remaining methods are order-aware.
    # Big-O running times for all methods are the same as for regular dictionaries.

    # The internal self.__map dictionary maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # Each link is stored as a list of length three:  [PREV, NEXT, KEY].

    def __init__(self, *args, **kwds):
        '''Initialize an ordered dictionary.  Signature is the same as for
        regular dictionaries, but keyword arguments are not recommended
        because their insertion order is arbitrary.

        '''
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__root
        except AttributeError:
            self.__root = root = [None, None, None]     # sentinel node
            PREV = 0
            NEXT = 1
            root[PREV] = root[NEXT] = root
            self.__map = {}
        self.__lower = {}
        self.update(*args, **kwds)

    def __setitem__(self, key, value, PREV=0, NEXT=1, dict_setitem=dict.__setitem__):
        'od.__setitem__(i, y) <==> od[i]=y'
        # Setting a new item creates a new link which goes at the end of the linked
        # list, and the inherited dictionary is updated with the new key/value pair.
        if key not in self:
            root = self.__root
            last = root[PREV]
            last[NEXT] = root[PREV] = self.__map[key] = [last, root, key]
            self.__lower[key.lower()] = key
        key = self.__lower[key.lower()]
        dict_setitem(self, key, value)

    def __delitem__(self, key, PREV=0, NEXT=1, dict_delitem=dict.__delitem__):
        'od.__delitem__(y) <==> del od[y]'
        # Deleting an existing item uses self.__map to find the link which is
        # then removed by updating the links in the predecessor and successor nodes.
        if key in self:
            key = self.__lower.pop(key.lower())

        dict_delitem(self, key)
        link = self.__map.pop(key)
        link_prev = link[PREV]
        link_next = link[NEXT]
        link_prev[NEXT] = link_next
        link_next[PREV] = link_prev

    def __getitem__(self, key, dict_getitem=dict.__getitem__):
        if key in self:
            key = self.__lower.get(key.lower())
        return dict_getitem(self, key)

    def __contains__(self, key):
        return key.lower() in self.__lower

    def __iter__(self, NEXT=1, KEY=2):
        'od.__iter__() <==> iter(od)'
        # Traverse the linked list in order.
        root = self.__root
        curr = root[NEXT]
        while curr is not root:
            yield curr[KEY]
            curr = curr[NEXT]

    def __reversed__(self, PREV=0, KEY=2):
        'od.__reversed__() <==> reversed(od)'
        # Traverse the linked list in reverse order.
        root = self.__root
        curr = root[PREV]
        while curr is not root:
            yield curr[KEY]
            curr = curr[PREV]

    def __reduce__(self):
        'Return state information for pickling'
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__root
        del self.__map, self.__root
        inst_dict = vars(self).copy()
        self.__map, self.__root = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def clear(self):
        'od.clear() -> None.  Remove all items from od.'
        try:
            for node in self.__map.values():
                del node[:]
            self.__root[:] = [self.__root, self.__root, None]
            self.__map.clear()
        except AttributeError:
            pass
        dict.clear(self)

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    setdefault = MutableMapping.setdefault
    update = MutableMapping.update
    pop = MutableMapping.pop
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items
    __ne__ = MutableMapping.__ne__

    def popitem(self, last=True):
        '''od.popitem() -> (k, v), return and remove a (key, value) pair.
        Pairs are returned in LIFO order if last is true or FIFO order if false.

        '''
        if not self:
            raise KeyError('dictionary is empty')
        key = next(reversed(self) if last else iter(self))
        value = self.pop(key)
        return key, value

    def __repr__(self):
        'od.__repr__() <==> repr(od)'
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, list(self.items()))

    def copy(self):
        'od.copy() -> a shallow copy of od'
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        '''OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S
        and values equal to v (which defaults to None).

        '''
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        '''od.__eq__(y) <==> od==y.  Comparison to another OD is order-sensitive
        while comparison to a regular mapping is order-insensitive.

        '''
        if isinstance(other, IOrderedDict):
            return len(self)==len(other) and \
                    set(self.items()) == set(other.items())
        return dict.__eq__(self, other)

    def __del__(self):
        self.clear()                # eliminate cyclical references


status_reasons = {
    # Status Codes
    # Informational
    100: 'Continue',
    101: 'Switching Protocols',
    102: 'Processing',

    # Successful
    200: 'OK',
    201: 'Created',
    202: 'Accepted',
    203: 'Non Authoritative Information',
    204: 'No Content',
    205: 'Reset Content',
    206: 'Partial Content',
    207: 'Multi Status',
    226: 'IM Used',

    # Redirection
    300: 'Multiple Choices',
    301: 'Moved Permanently',
    302: 'Found',
    303: 'See Other',
    304: 'Not Modified',
    305: 'Use Proxy',
    307: 'Temporary Redirect',

    # Client Error
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request URI Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    422: 'Unprocessable Entity',
    423: 'Locked',
    424: 'Failed Dependency',
    426: 'Upgrade Required',

    # Server Error
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'HTTP Version Not Supported',
    507: 'Insufficient Storage',
    510: 'Not Extended',
}



METHOD_RE = re.compile("[A-Z0-9$-_.]{3,20}")
VERSION_RE = re.compile("HTTP/(\d+).(\d+)")
STATUS_RE = re.compile("(\d{3})\s*(\w*)")
HEADER_RE = re.compile("[\x00-\x1F\x7F()<>@,;:\[\]={} \t\\\\\"]")

# errors
BAD_FIRST_LINE = 0
INVALID_HEADER = 1
INVALID_CHUNK = 2

class InvalidRequestLine(Exception):
    """ error raised when first line is invalid """

class InvalidHeader(Exception):
    """ error raised on invalid header """

class InvalidChunkSize(Exception):
    """ error raised when we parse an invalid chunk size """

class HttpParser(object):

    def __init__(self, kind=2, decompress=False):
        self.kind = kind
        self.decompress = decompress

        # errors vars
        self.errno = None
        self.errstr = ""

        # protected variables
        self._buf = []
        self._version = None
        self._method = None
        self._status_code = None
        self._status = None
        self._reason = None
        self._url = None
        self._path = None
        self._query_string = None
        self._fragment= None
        self._headers = IOrderedDict()
        self._environ = dict()
        self._chunked = False
        self._body = []
        self._trailers = None
        self._partial_body = False
        self._clen = None
        self._clen_rest = None

        # private events
        self.__on_firstline = False
        self.__on_headers_complete = False
        self.__on_message_begin = False
        self.__on_message_complete = False

        self.__decompress_obj = None
        self.__decompress_first_try = True

    def get_version(self):
        return self._version

    def get_method(self):
        return self._method

    def get_status_code(self):
        return self._status_code

    def get_url(self):
        return self._url

    def get_path(self):
        return self._path

    def get_query_string(self):
        return self._query_string

    def get_fragment(self):
        return self._fragment

    def get_headers(self):
        return self._headers

    def get_wsgi_environ(self):
        if not self.__on_headers_complete:
            return None

        environ = self._environ.copy()
        # clean special keys
        for key in ("CONTENT_LENGTH", "CONTENT_TYPE", "SCRIPT_NAME"):
            hkey = "HTTP_%s" % key
            if hkey in environ:
                environ[key] = environ.pop(hkey)

        script_name = environ.get('SCRIPT_NAME',
                os.environ.get("SCRIPT_NAME", ""))
        if script_name:
            path_info = self._path.split(script_name, 1)[1]
            environ.update({
                "PATH_INFO": unquote(path_info),
                "SCRIPT_NAME": script_name})
        else:
            environ['SCRIPT_NAME'] = ""

        if environ.get('HTTP_X_FORWARDED_PROTOCOL', '').lower() == "ssl":
            environ['wsgi.url_scheme'] = "https"
        elif environ.get('HTTP_X_FORWARDED_SSL', '').lower() == "on":
            environ['wsgi.url_scheme'] = "https"
        else:
            environ['wsgi.url_scheme'] = "http"

        return environ

    def recv_body(self):
        """ return last chunk of the parsed body"""
        body = b("").join(self._body)
        self._body = []
        self._partial_body = False
        return body

    def recv_body_into(self, barray):
        """ Receive the last chunk of the parsed body and store the data
        in a buffer rather than creating a new string. """
        l = len(barray)
        body = b("").join(self._body)
        m = min(len(body), l)
        data, rest = body[:m], body[m:]
        barray[0:m] = data
        if not rest:
            self._body = []
            self._partial_body = False
        else:
            self._body = [rest]
        return m

    def is_upgrade(self):
        """ Do we get upgrade header in the request. Useful for
        websockets """
        hconn = self._headers.get('connection', "").lower()
        hconn_parts = [x.strip() for x in hconn.split(',')]
        return "upgrade" in hconn_parts

    def is_headers_complete(self):
        """ return True if all headers have been parsed. """
        return self.__on_headers_complete

    def is_partial_body(self):
        """ return True if a chunk of body have been parsed """
        return self._partial_body

    def is_message_begin(self):
        """ return True if the parsing start """
        return self.__on_message_begin

    def is_message_complete(self):
        """ return True if the parsing is done (we get EOF) """
        return self.__on_message_complete

    def is_chunked(self):
        """ return True if Transfer-Encoding header value is chunked"""
        return self._chunked

    def should_keep_alive(self):
        """ return True if the connection should be kept alive
        """
        hconn = self._headers.get('connection', "").lower()
        if hconn == "close":
            return False
        elif hconn == "keep-alive":
            return True
        return self._version == (1, 1)

    def execute(self, data, length):
        # end of body can be passed manually by putting a length of 0

        if length == 0:
            self.__on_message_complete = True
            return length

        # start to parse
        nb_parsed = 0
        while True:
            if not self.__on_firstline:
                idx = data.find(b("\r\n"))
                if idx < 0:
                    self._buf.append(data)
                    return len(data)
                else:
                    self.__on_firstline = True
                    self._buf.append(data[:idx])
                    first_line = bytes_to_str(b("").join(self._buf))
                    nb_parsed = nb_parsed + idx + 2

                    rest = data[idx+2:]
                    data = b("")
                    if self._parse_firstline(first_line):
                        self._buf = [rest]
                    else:
                        return nb_parsed
            elif not self.__on_headers_complete:
                if data:
                    self._buf.append(data)
                    data = b("")

                try:
                    to_parse = b("").join(self._buf)
                    ret = self._parse_headers(to_parse)

                    if ret is False:
                        return length
                    nb_parsed = nb_parsed + (len(to_parse) - ret)
                except InvalidHeader as e:
                    self.errno = INVALID_HEADER
                    self.errstr = str(e)
                    return nb_parsed
            elif not self.__on_message_complete:
                if not self.__on_message_begin:
                    self.__on_message_begin = True

                if data:
                    self._buf.append(data)
                    data = b("")

                ret = self._parse_body()
                if ret is None:
                    return length

                elif ret < 0:
                    return ret
                elif ret == 0:
                    self.__on_message_complete = True
                    return length
                else:
                    nb_parsed = max(length, ret)

            else:
                return 0

    def _parse_firstline(self, line):
        try:
            if self.kind == 2: # auto detect
                try:
                    self._parse_request_line(line)
                except InvalidRequestLine:
                    self._parse_response_line(line)
            elif self.kind == 1:
                self._parse_response_line(line)
            elif self.kind == 0:
                self._parse_request_line(line)
        except InvalidRequestLine as e:
            self.errno = BAD_FIRST_LINE
            self.errstr = str(e)
            return False
        return True

    def _parse_response_line(self, line):
        bits = line.split(None, 1)
        if len(bits) != 2:
            raise InvalidRequestLine(line)

        # version
        matchv = VERSION_RE.match(bits[0])
        if matchv is None:
            raise InvalidRequestLine("Invalid HTTP version: %s" % bits[0])
        self._version = (int(matchv.group(1)), int(matchv.group(2)))

        # status
        matchs = STATUS_RE.match(bits[1])
        if matchs is None:
            raise InvalidRequestLine("Invalid status %" % bits[1])

        self._status = bits[1]
        self._status_code = int(matchs.group(1))
        self._reason = matchs.group(2)

    def _parse_request_line(self, line):
        bits = line.split(None, 2)
        if len(bits) != 3:
            raise InvalidRequestLine(line)

        # Method
        if not METHOD_RE.match(bits[0]):
            raise InvalidRequestLine("invalid Method: %s" % bits[0])
        self._method = bits[0].upper()

        # URI
        self._url = bits[1]
        parts = urlparse.urlsplit(bits[1])
        self._path = parts.path or ""
        self._query_string = parts.query or ""
        self._fragment = parts.fragment or ""

        # Version
        match = VERSION_RE.match(bits[2])
        if match is None:
            raise InvalidRequestLine("Invalid HTTP version: %s" % bits[2])
        self._version = (int(match.group(1)), int(match.group(2)))

        # update environ
        if hasattr(self,'_environ'):
            self._environ.update({
                "PATH_INFO": self._path,
                "QUERY_STRING": self._query_string,
                "RAW_URI": self._url,
                "REQUEST_METHOD": self._method,
                "SERVER_PROTOCOL": bits[2]})

    def _parse_headers(self, data):
        if data == b'\r\n':
            self.__on_headers_complete = True
            self._buf = []
            return 0
        idx = data.find(b("\r\n\r\n"))
        if idx < 0: # we don't have all headers
            if self._status_code == 204 and data == b("\r\n"):
                self._buf = []
                self.__on_headers_complete = True
                return 0
            else:
                return False

        # Split lines on \r\n keeping the \r\n on each line
        lines = [bytes_to_str(line) + "\r\n" for line in
                data[:idx].split(b("\r\n"))]

        # Parse headers into key/value pairs paying attention
        # to continuation lines.
        while len(lines):
            # Parse initial header name : value pair.
            curr = lines.pop(0)
            if curr.find(":") < 0:
                raise InvalidHeader("invalid line %s" % curr.strip())
            name, value = curr.split(":", 1)
            name = name.rstrip(" \t").upper()
            if HEADER_RE.search(name):
                raise InvalidHeader("invalid header name %s" % name)

            if value.endswith("\r\n"):
                value = value[:-2]

            name, value = name.strip(), [value.lstrip()]

            # Consume value continuation lines
            while len(lines) and lines[0].startswith((" ", "\t")):
                curr = lines.pop(0)
                if curr.endswith("\r\n"):
                    curr = curr[:-2]
                value.append(curr)
            value = ''.join(value).rstrip()

            # multiple headers
            if name in self._headers:
                value = "%s, %s" % (self._headers[name], value)

            # store new header value
            self._headers[name] = value

            # update WSGI environ
            key =  'HTTP_%s' % name.upper().replace('-','_')
            self._environ[key] = value

        # detect now if body is sent by chunks.
        clen = self._headers.get('content-length')
        te = self._headers.get('transfer-encoding', '').lower()

        if clen is not None:
            try:
                self._clen_rest = self._clen = int(clen)
            except ValueError:
                pass
        else:
            self._chunked = (te == 'chunked')
            if not self._chunked:
                self._clen_rest = MAXSIZE

        # detect encoding and set decompress object
        encoding = self._headers.get('content-encoding')
        if self.decompress:
            if encoding == "gzip":
                self.__decompress_obj = zlib.decompressobj(16+zlib.MAX_WBITS)
                self.__decompress_first_try = False
            elif encoding == "deflate":
                self.__decompress_obj = zlib.decompressobj()

        rest = data[idx+4:]
        self._buf = [rest]
        self.__on_headers_complete = True
        return len(rest)

    def _parse_body(self):
        if self._status_code == 204 and len(self._buf) == 0:
            self.__on_message_complete = True
            return
        elif not self._chunked:
            body_part = b("").join(self._buf)
            #
            if not body_part and self._clen is None:
                if not self._status: # message complete only for servers
                    self.__on_message_complete = True
                return
            self._clen_rest -= len(body_part)

            # maybe decompress
            if self.__decompress_obj is not None:
                if not self.__decompress_first_try:
                    body_part = self.__decompress_obj.decompress(body_part)
                else:
                    try:
                        body_part = self.__decompress_obj.decompress(body_part)
                    except zlib.error:
                        self.__decompress_obj.decompressobj = zlib.decompressobj(-zlib.MAX_WBITS)
                        body_part = self.__decompress_obj.decompress(body_part)
                    self.__decompress_first_try = False


            self._partial_body = True
            self._body.append(body_part)
            self._buf = []

            if self._clen_rest <= 0:
                self.__on_message_complete = True
            return
        else:
            data = b("").join(self._buf)
            try:

                size, rest = self._parse_chunk_size(data)
            except InvalidChunkSize as e:
                self.errno = INVALID_CHUNK
                self.errstr = "invalid chunk size [%s]" % str(e)
                return -1

            if size == 0:
                return size

            if size is None or len(rest) < size + 2:  # wait till terminator
                return None


            body_part, rest = rest[:size], rest[size:]
            if len(rest) < 2:
                self.errno = INVALID_CHUNK
                self.errstr = "chunk missing terminator [%s]" % data
                return -1

            # maybe decompress
            if self.__decompress_obj is not None:
                body_part = self.__decompress_obj.decompress(body_part)

            self._partial_body = True
            self._body.append(body_part)

            self._buf = [rest[2:]]
            return len(rest)

    def _parse_chunk_size(self, data):
        idx = data.find(b("\r\n"))
        if idx < 0:
            return None, None
        line, rest_chunk = data[:idx], data[idx+2:]
        chunk_size = line.split(b(";"), 1)[0].strip()
        try:
            chunk_size = int(chunk_size, 16)
        except ValueError:
            raise InvalidChunkSize(chunk_size)

        if chunk_size == 0:
            self._parse_trailers(rest_chunk)
            return 0, None
        return chunk_size, rest_chunk

    def _parse_trailers(self, data):
        idx = data.find(b("\r\n\r\n"))

        if data[:2] == b("\r\n"):
            self._trailers = self._parse_headers(data[:idx])
            
import json
from urllib.parse import parse_qsl
from dataclasses import dataclass

@dataclass
class HttpMessage():
    fragment: str
    headers: Dict[str, str]
    method: str
    parameters: Dict[str, str]
    path: str
    query_string: str
    raw_body: bytes
    status_code: int
    url: str
    version: str

class HttpMessageParser(HttpParser):
    def __init__(self, data:bytes, decompress_body=True):
        super().__init__(decompress = decompress_body)
        self.execute(data, len(data))
        self._parameters  = {}
        try:
            self._parse_parameters()
        except Exception as e:
            print("Error in parameters parsing:", data)
            print("Exception:", str(e))

    def get_raw_body(self) -> bytes:
        return b"\r\n".join(self._body)
    
    def _parse_query_string(self, raw_string):
        parameters = parse_qsl(raw_string)
        for key,value in parameters:
            try:
                key = key.decode()
                value = value.decode()
            except:
                pass
            if self._parameters.get(key):
                if isinstance(self._parameters[key], list):
                    self._parameters[key].append(value)
                else:
                    self._parameters[key] = [self._parameters[key], value]
            else:
                self._parameters[key] = value

    def _parse_parameters(self):
        if self._method == "POST":
            body = self.get_raw_body()
            if len(body) == 0:
                return
            content_type = self.get_headers().get("Content-Type")
            if not content_type or "x-www-form-urlencoded" in content_type:
                try:
                    self._parse_query_string(body.decode())
                except:
                    pass
            elif "json" in content_type:
                self._parameters = json.loads(body)
        elif self._method == "GET":
            self._parse_query_string(self._query_string)
        
    def get_parameters(self) ->Dict[str, str]:
        """returns parameters parsed from query string or body"""
        return self._parameters
    
    def get_version(self) -> str:
        if self._version:
            return ".".join([str(x) for x in self._version])
        return None

    def to_message(self) -> HttpMessage:
        return HttpMessage(self._fragment, self._headers, self._method,
                           self._parameters, self._path, self._query_string,
                           self.get_raw_body(), self._status_code,
                           self._url, self.get_version()
                           )