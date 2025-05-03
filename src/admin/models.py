from pydantic import BaseModel, Field


class Config(BaseModel):
    proxy_host: str             = Field(...,                 description="Host that the proxy will run on")
    proxy_port: int             = Field(..., gt=0, le=65535, description="Port that the proxy will run on")

    real_host: str              = Field(...,                 description="Host that the real server is running on")
    real_port: int              = Field(..., gt=0, le=65535, description="Port that the real server is running on")


    max_bytes_per_request:  int | None      = Field(None, ge=0, description="Maximum number of bytes per request")
    max_bytes_per_response: int | None      = Field(None, ge=0, description="Maximum number of bytes per response")
    max_requests_per_second: float | None   = Field(None, ge=0, description="Maximum number of requests per second")
