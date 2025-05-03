from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from proxy_manager import ProxyNotFound, proxy_manager

# Initialize app
app = FastAPI()

# Serve pages directory as a static site
app.mount("/pages", StaticFiles(directory="admin/pages"), "pages")


# Endpoint to spawn instance of proxy
@app.post("/proxy/new", tags=["Proxy management"])
async def new_proxy() -> int:
    return await proxy_manager.new()


# Endpoint to delete an instance of a proxy
@app.delete("/proxy/{proxy_id}", tags=["Proxy management"])
async def terminate_proxy(proxy_id: int):
    try:
        proxy_manager.terminate(proxy_id)
    except ProxyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


# Clean up proxies on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before shutdown
    yield
    # During shutdown
    proxy_manager.cleanup()
