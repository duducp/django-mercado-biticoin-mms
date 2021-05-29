from ninja import Schema


class PingOutSchema(Schema):
    message: str
    version: str
    timestamp: int
    host: str
