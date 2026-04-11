from enum import Enum

# General
CRLF = "\r\n"
ENCODING = "iso-8859-1"

# Client
DEFAULT_BUFFER_SIZE = 4096
DEFAULT_PORT = 80

# Server
DEFAULT_LISTENING_PORT = 28333
DEFAULT_BUFFER_SIZE = 4096


class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    DELETE = "DELETE"


class ContentType(Enum):
    TEXT_PLAIN = "text/plain"
    TEXT_HTML = "text/html"
    JSON = "application/json"
