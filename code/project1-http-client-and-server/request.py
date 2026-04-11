import re

from constants import CRLF, ENCODING
from errors import InvalidRequestException


class Request:
    DEFAULT_METHOD = "GET"
    DEFAULT_PATH = "/"
    DEFAULT_VERSION = "HTTP/1.1"
    DEFAULT_HOST = "localhost"

    def __init__(
        self,
        method=None,
        path=None,
        version=None,
        host=None,
        payload=None,
    ):
        # Fall back to class constants if no value is provided
        self.__method = method or self.DEFAULT_METHOD
        self.__path = path or self.DEFAULT_PATH
        self.__version = version or self.DEFAULT_VERSION
        self.__host = host or self.DEFAULT_HOST
        self.__payload = payload

    @property
    def method(self):
        return self.__method

    @property
    def path(self):
        return self.__path

    @property
    def version(self):
        return self.__version

    @property
    def payload(self):
        return self.__payload

    @property
    def host(self):
        return self.__host

    # Raises InvalidRequestException if specified content length is less than
    # the actual length of the payload
    @staticmethod
    def is_data_receiving_done(total_bytes: bytes):
        # Decode the bytes
        data = total_bytes.decode(ENCODING)

        # If the empty line has not been received yet, we can return false
        double_crlf_index = data.find(CRLF * 2)
        if double_crlf_index == -1:
            return False

        # At this point we know that atleast the empty line after the headers
        # have been received. So we can parse the content length.
        # Content-Length:  24   \r\n
        # There could be white spaces before and after the number
        # and content-length itself could be lowercase
        match = re.search(r"Content-Length:\s*(\d+)", data, re.IGNORECASE)

        # If content-length header is not there, we can return true
        # as at this point, we have the double CRLF
        if not match:
            return True

        # At this point we can extract the content length
        content_length = int(match.group(1))

        # We can now check if the number of bytes after the empty line is
        # equal to the content length
        payload_start_index = double_crlf_index + len(CRLF * 2)
        num_bytes_payload = len(data[payload_start_index:].encode(ENCODING))

        # If the number of bytes in the payload is more than what the content length
        # specifies, we throw an error
        if num_bytes_payload > content_length:
            raise InvalidRequestException(
                "Payload length more than content length specified."
            )

        return num_bytes_payload == content_length

    def __str__(self):
        s = f"{self.__method} {self.__path} {self.__version}{CRLF}"
        s += f"Host: {self.__host}{CRLF}"
        s += f"Connection: close{CRLF}"
        s += CRLF

        if self.__payload:
            s += self.__payload

        return s

    @classmethod
    def from_raw_data(cls, data: str):
        # At this point we know that the request data is valid

        # Get the request method, path and version
        # Eg: "GET /index.html HTTP/1.1"
        match = re.search(
            r"^\s*(GET|POST|DELETE)\s+(/\S*)\s+(HTTP/\d\.\d)",
            data,
            re.IGNORECASE,
        )

        # If not a match, then we can throw error
        if not match:
            raise InvalidRequestException("Not a valid request.")

        # Extract the method, path and version
        method = match.group(1).upper()
        path = match.group(2)
        version = match.group(3).upper()

        # Extract the host
        match = re.search(r"Host:\s*(\S*)", data, re.IGNORECASE)
        host = match.group(1)

        # Check if the content length header exists
        double_crlf_index = data.find(CRLF * 2)
        match = re.search(r"Content-Length:\s*(\d+)", data, re.IGNORECASE)
        if not match:
            payload = None
        else:
            # Get the exact number of bytes as the content-length
            content_length = int(match.group(1))
            payload_start_index = double_crlf_index + len(CRLF * 2)
            payload = (
                data[payload_start_index:]
                .encode(ENCODING)[:content_length]
                .decode(ENCODING)
            )

        return cls(
            method=method, path=path, version=version, payload=payload, host=host
        )

    def get_bytes(self):
        return self.__str__().encode(ENCODING)


class RequestBuilder:
    def __init__(self):
        self.method = Request.DEFAULT_METHOD
        self.path = Request.DEFAULT_PATH
        self.version = Request.DEFAULT_VERSION
        self.host = Request.DEFAULT_HOST
        self.payload = None

    def set_method(self, method):
        self.method = method
        return self

    def set_path(self, path):
        self.path = path
        return self

    def set_host(self, host):
        self.host = host
        return self

    def set_version(self, version):
        self.version = version
        return self

    def set_payload(self, payload):
        self.payload = payload
        return self

    def build(self) -> Request:
        #
        return Request(
            method=self.method,
            path=self.path,
            version=self.version,
            payload=self.payload,
            host=self.host,
        )
