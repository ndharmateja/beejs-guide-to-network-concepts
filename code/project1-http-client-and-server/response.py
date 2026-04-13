import re

from constants import CRLF, ENCODING, ContentType
from errors import InvalidResponseException


class ResponseBuilder:
    def __init__(self):
        self.status_code = Response.DEFAULT_STATUS_CODE
        self.status_message = Response.DEFAULT_STATUS_MESSAGE
        self.version = Response.DEFAULT_VERSION
        self.content_bytes = b""
        self.content_type = Response.DEFAULT_CONTENT_TYPE

    def set_status(self, code: int, message: str):
        self.status_code = code
        self.status_message = message
        return self

    def set_version(self, version: str):
        self.version = version
        return self

    def set_content_bytes(self, content_bytes: bytes, content_type: ContentType = None):
        self.content_bytes = content_bytes
        if content_type:
            if not isinstance(content_type, ContentType):
                raise TypeError("content_type must be a valid ContentType enum")
            self.content_type = content_type
        return self

    def build(self) -> "Response":
        return Response(
            status_code=self.status_code,
            status_message=self.status_message,
            version=self.version,
            content_bytes=self.content_bytes,
            content_type=self.content_type,
        )


class Response:
    DEFAULT_VERSION = "HTTP/1.1"
    DEFAULT_STATUS_CODE = 200
    DEFAULT_STATUS_MESSAGE = "OK"
    DEFAULT_CONTENT_TYPE = ContentType.TEXT_PLAIN

    def __init__(
        self,
        status_code: int = None,
        status_message: str = None,
        version: str = None,
        content_bytes: bytes = None,
        content_type: ContentType = None,
    ):
        self.__status_code = status_code or self.DEFAULT_STATUS_CODE
        self.__status_message = status_message or self.DEFAULT_STATUS_MESSAGE
        self.__version = version or self.DEFAULT_VERSION
        self.__content_bytes = content_bytes or b""
        self.__content_type = content_type or self.DEFAULT_CONTENT_TYPE

    @property
    def status_code(self) -> int:
        return self.__status_code

    @property
    def status_message(self) -> str:
        return self.__status_message

    @property
    def version(self) -> str:
        return self.__version

    @property
    def content_bytes(self) -> bytes:
        return self.__content_bytes

    @property
    def content_type(self) -> ContentType:
        return self.__content_type

    @classmethod
    def create_404_response(cls):
        return cls(
            status_code=404,
            status_message="Not Found",
            content_bytes="404 not found".encode(ENCODING),
        )

    @classmethod
    def create_400_response(cls, message: str = "Bad Request"):
        return cls(
            status_code=400,
            status_message="Bad Request",
            content_bytes=message.encode(ENCODING),
        )

    @classmethod
    def create_415_response(cls, message: str = "Unsupported Media Type"):
        return cls(
            status_code=415,
            status_message="Unsupported Media Type",
            content_bytes=message.encode(ENCODING),
        )

    @classmethod
    def create_500_response(cls, message: str = "Internal Server Error"):
        return cls(
            status_code=500,
            status_message="Internal Server Error",
            content_bytes=message.encode(ENCODING),
        )

    @classmethod
    def from_raw_data(cls, raw_bytes: bytes):
        """
        Parses raw bytes into a Response object.
        Useful for the WebClient receiving data from a server.
        """
        # 1. Separate Headers and Body
        double_crlf_bytes = (CRLF * 2).encode(ENCODING)
        boundary_index = raw_bytes.find(double_crlf_bytes)

        if boundary_index == -1:
            header_text = raw_bytes.decode(ENCODING)
            body_bytes = b""
        else:
            header_text = raw_bytes[:boundary_index].decode(ENCODING)
            body_bytes = raw_bytes[boundary_index + len(double_crlf_bytes) :]

        # 2. Parse Status Line (e.g., HTTP/1.1 200 OK)
        line_match = re.search(r"(HTTP/\d\.\d)\s+(\d+)\s+(.*)", header_text)
        if not line_match:
            raise InvalidResponseException("Invalid HTTP Response Status Line")

        # Parse Content-Type header
        ct_match = re.search(r"Content-Type:\s*([^;\r\n]+)", header_text, re.IGNORECASE)
        content_type = cls.DEFAULT_CONTENT_TYPE
        if ct_match:
            try:
                content_type = ContentType(ct_match.group(1).strip().lower())
            except ValueError:
                pass

        return cls(
            version=line_match.group(1),
            status_code=int(line_match.group(2)),
            status_message=line_match.group(3).strip(),
            content_bytes=body_bytes,
            content_type=content_type,
        )

    def __str__(self):
        # We decode only for the string representation
        body_text = self.__content_bytes.decode(ENCODING)
        return (
            f"{self.__version} {self.__status_code} {self.__status_message}\n"
            f"Content-Type: {self.__content_type.value}\n"
            f"Content-Length: {len(self.__content_bytes)}\n"
            f"Body: {body_text}"
        )

    def get_bytes(self):
        header_str = (
            f"{self.__version} {self.__status_code} {self.__status_message}{CRLF}"
        )
        header_str += f"Content-Type: {self.__content_type.value}{CRLF}"
        header_str += f"Content-Length: {len(self.__content_bytes)}{CRLF}"
        header_str += f"Connection: close{CRLF}"
        header_str += CRLF

        return header_str.encode(ENCODING) + self.__content_bytes
