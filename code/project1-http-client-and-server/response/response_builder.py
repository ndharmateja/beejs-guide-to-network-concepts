from constants import ContentType
from response import Response


class ResponseBuilder:
    def __init__(self):
        self.status_code = Response.DEFAULT_STATUS_CODE
        self.status_message = Response.DEFAULT_STATUS_MESSAGE
        self.version = Response.DEFAULT_VERSION
        self.content = ""
        self.content_type = Response.DEFAULT_CONTENT_TYPE

    def set_status(self, code: int, message: str):
        self.status_code = code
        self.status_message = message
        return self

    def set_version(self, version: str):
        self.version = version
        return self

    def set_content(self, content: str, content_type: ContentType = None):
        self.content = content
        if content_type:
            if not isinstance(content_type, ContentType):
                raise TypeError("content_type must be a valid ContentType enum")
            self.content_type = content_type
        return self

    def build(self) -> Response:
        return Response(
            status_code=self.status_code,
            status_message=self.status_message,
            version=self.version,
            content=self.content,
            content_type=self.content_type,
        )
