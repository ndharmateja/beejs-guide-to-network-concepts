import re

from constants import CRLF, ENCODING
from errors import InvalidRequestException


class Request:
    # Raises InvalidRequestException if specified content length is less than
    # the actual length of the payload
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

    def __init__(self, data: str):
        # At this point we know that the request data is valid

        # Get the request method, path and version
        # Eg: "GET /index.html HTTP/1.1"
        match = re.search(
            r"^\s*(GET|POST|DELETE)\s+(/\S+)\s+(HTTP/\d\.\d)",
            data,
            re.IGNORECASE,
        )

        # If not a match, then we can throw error
        if not match:
            raise InvalidRequestException("Not a valid request.")

        # Extract the method, path and version
        self.method = match.group(1).upper()
        self.path = match.group(2)
        self.version = match.group(3).upper()

        # Check if the content length header exists
        double_crlf_index = data.find(CRLF * 2)
        match = re.search(r"Content-Length:\s*(\d+)", data, re.IGNORECASE)
        if not match:
            self.payload = None
        else:
            # Get the exact number of bytes as the content-length
            content_length = int(match.group(1))
            payload_start_index = double_crlf_index + len(CRLF * 2)
            self.payload = (
                data[payload_start_index:]
                .encode(ENCODING)[:content_length]
                .decode(ENCODING)
            )
