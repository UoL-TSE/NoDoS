from pydantic import BaseModel, Field


class Config(BaseModel):
    name: str                   = Field(..., max_length=64,  description="Name to save the config under")
    proxy_host: str             = Field(...,                 description="Host that the proxy will run on")
    proxy_port: int             = Field(..., gt=0, le=65535, description="Port that the proxy will run on")

    real_host: str              = Field(...,                 description="Host that the real server is running on")
    real_port: int              = Field(..., gt=0, le=65535, description="Port that the real server is running on")


    max_bytes_per_request:  int | None      = Field(None, ge=0, description="Maximum number of bytes per request")
    max_bytes_per_response: int | None      = Field(None, ge=0, description="Maximum number of bytes per response")
    max_requests_per_second: float | None   = Field(None, ge=0, description="Maximum number of requests per second")


class MetaConfig(BaseModel):
    config_id: int                          = Field(..., description="Unique identifier for the config")
    config_name: str                        = Field(..., description="Configuration name")


class Configs(BaseModel):
    configs: list[MetaConfig]             = Field(..., description="List of config names with their respective ids")

class Proxy(BaseModel):
    proxy_id: int                          = Field(..., description="Unique identifier for the proxy")
    status: bool                           = Field(..., description="Status of the proxy")
    exit_code: int | None                  = Field(None, description="Exit code of the proxy if it has exited") 

class Proxies(BaseModel):
    proxies: list[Proxy]                  = Field(..., description="List of proxies with their respective ids and status")