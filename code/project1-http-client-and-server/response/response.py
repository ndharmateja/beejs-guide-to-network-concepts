import re

from constants import CRLF, ENCODING, ContentType
from errors import InvalidResponseException


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
        content: str = None,
        content_type: ContentType = None,
    ):
        self.__status_code = status_code or self.DEFAULT_STATUS_CODE
        self.__status_message = status_message or self.DEFAULT_STATUS_MESSAGE
        self.__version = version or self.DEFAULT_VERSION
        self.__content = content or ""
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
    def content(self) -> str:
        return self.__content

    @property
    def content_type(self) -> ContentType:
        return self.__content_type

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
            # If no double CRLF, it might just be a status line or partial
            header_text = raw_bytes.decode(ENCODING)
            body_text = ""
        else:
            header_text = raw_bytes[:boundary_index].decode(ENCODING)
            body_text = raw_bytes[boundary_index + len(double_crlf_bytes) :].decode(
                ENCODING
            )

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
            content=body_text,
            content_type=content_type,
        )

    def __str__(self):
        return (
            f"{self.__version} {self.__status_code} {self.__status_message}\n"
            f"Content-Type: {self.__content_type.value}\n"
            f"Content-Length: {len(self.__content.encode(ENCODING))}\n"
            f"Body: {self.__content}"
        )

    def get_bytes(self):
        # Calculate content length in bytes to be encoding-safe
        body_bytes = self.__content.encode(ENCODING)

        header_str = (
            f"{self.__version} {self.__status_code} {self.__status_message}{CRLF}"
        )
        header_str += f"Content-Type: {self.__content_type.value}{CRLF}"
        header_str += f"Content-Length: {len(body_bytes)}{CRLF}"
        header_str += f"Connection: close{CRLF}"
        header_str += CRLF

        return header_str.encode(ENCODING) + body_bytes
