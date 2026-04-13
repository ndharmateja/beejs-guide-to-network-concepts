import re

from constants import CRLF, ENCODING, ContentType, HttpMethod
from errors import InvalidRequestException


class RequestBuilder:
    def __init__(self):
        self.method = Request.DEFAULT_METHOD
        self.path = Request.DEFAULT_PATH
        self.version = Request.DEFAULT_VERSION
        self.host = Request.DEFAULT_HOST
        self.payload = None
        self.content_type = Request.DEFAULT_CONTENT_TYPE

    def set_method(self, method: HttpMethod) -> "RequestBuilder":
        if not isinstance(method, HttpMethod):
            raise TypeError("Method must be a valid HttpMethod enum")
        self.method = method
        return self

    def set_path(self, path: str) -> "RequestBuilder":
        self.path = path
        return self

    def set_host(self, host: str) -> "RequestBuilder":
        self.host = host
        return self

    def set_version(self, version: str) -> "RequestBuilder":
        self.version = version
        return self

    def set_payload(self, payload: str) -> "RequestBuilder":
        self.payload = payload
        return self

    def set_content_type(self, content_type: ContentType) -> "RequestBuilder":
        if not isinstance(content_type, ContentType):
            raise TypeError("Content type must be a valid ContentType enum")
        self.content_type = content_type
        return self

    def build(self) -> "Request":
        return Request(
            method=self.method,
            path=self.path,
            version=self.version,
            payload=self.payload,
            host=self.host,
            content_type=self.content_type,
        )


class Request:
    DEFAULT_METHOD = HttpMethod.GET
    DEFAULT_PATH = "/"
    DEFAULT_VERSION = "HTTP/1.1"
    DEFAULT_HOST = "localhost"
    DEFAULT_CONTENT_TYPE = ContentType.TEXT_PLAIN

    def __init__(
        self,
        method: HttpMethod = None,
        path: str = None,
        version: str = None,
        host: str = None,
        payload: str = None,
        content_type: ContentType = None,
    ):
        # Fall back to class constants if no value is provided
        self.__method = method or self.DEFAULT_METHOD
        self.__path = path or self.DEFAULT_PATH
        self.__version = version or self.DEFAULT_VERSION
        self.__host = host or self.DEFAULT_HOST
        self.__payload = payload
        self.__content_type = content_type or self.DEFAULT_CONTENT_TYPE

    @property
    def method(self) -> HttpMethod:
        return self.__method

    @property
    def path(self) -> str:
        return self.__path

    @property
    def version(self) -> str:
        return self.__version

    @property
    def payload(self) -> str:
        return self.__payload

    @property
    def host(self) -> str:
        return self.__host

    @property
    def content_type(self) -> ContentType:
        return self.__content_type

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
        s = f"{self.__method.value} {self.__path} {self.__version}{CRLF}"
        s += f"Host: {self.__host}{CRLF}"
        s += f"Connection: close{CRLF}"
        # Add the content length and type headers if payload is present
        if self.__payload:
            payload_bytes = self.__payload.encode(ENCODING)
            s += f"Content-Length: {len(payload_bytes)}{CRLF}"
            s += f"Content-Type: {self.__content_type.value}{CRLF}"
        s += CRLF

        if self.__payload:
            s += self.__payload

        return s

    @classmethod
    def from_raw_data(cls, data: str):
        # At this point we know that the request data is valid

        # Get the request method, path and version
        # Eg: "GET /index.html HTTP/1.1"
        # methods_pattern will be "GET|POST|DELETE" based on the enum
        methods_pattern = "|".join([method.value for method in HttpMethod])
        match = re.search(
            rf"^\s*({methods_pattern})\s+(/\S*)\s+(HTTP/\d\.\d)",
            data,
            re.IGNORECASE,
        )

        # If not a match, then we can throw error
        if not match:
            raise InvalidRequestException("Not a valid request.")

        # Extract the method, path and version
        method_str = match.group(1).upper()
        path = match.group(2)
        version = match.group(3).upper()

        method = HttpMethod(method_str)

        # Extract the host
        match = re.search(r"Host:\s*(\S*)", data, re.IGNORECASE)
        host = match.group(1) if match else cls.DEFAULT_HOST

        # Create the request builder object
        req_builder = RequestBuilder()
        req_builder.set_path(path).set_method(method)
        req_builder.set_host(host).set_version(version)

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
            req_builder.set_payload(payload)

            # Get content type
            try:
                match = re.search(r"Content-Type:\s*(\S*)", data, re.IGNORECASE)
                content_type_str = match.group(1).lower()
                content_type = ContentType(content_type_str)
                req_builder.set_content_type(content_type)

            except ValueError:
                raise InvalidRequestException(
                    f"Invalid request. Invalid content type: {content_type_str}"
                )

        return req_builder.build()

    def get_bytes(self):
        return self.__str__().encode(ENCODING)
