from constants import ContentType, HttpMethod
from request import Request


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

    def build(self) -> Request:
        #
        return Request(
            method=self.method,
            path=self.path,
            version=self.version,
            payload=self.payload,
            host=self.host,
            content_type=self.content_type,
        )
