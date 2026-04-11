from constants import CRLF, ENCODING


class Response:
    def __init__(self, content):
        self.version = "HTTP/1.1"
        self.status_code = 200
        self.status_message = "OK"
        self.content = content

    def get_bytes(self):
        s = f"{self.version} {self.status_code} {self.status_message}{CRLF}"
        s += f"Content-Type: text/plain{CRLF}"
        s += f"Content-Length: {len(self.content.encode(ENCODING))}{CRLF}"
        s += f"Connection: close{CRLF}"
        s += CRLF
        s += self.content

        return s.encode(ENCODING)
