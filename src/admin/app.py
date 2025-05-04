from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from proxy_manager import ProxyNotFound, proxy_manager
from db import DB
from models import Config, Configs
from db_exceptions import ConfigNotFoundException

# Initialize app
app = FastAPI()

# Serve pages directory as a static site
admin_dir = Path(__file__).parent.absolute()
pages_dir = f"{admin_dir}/pages"
app.mount("/pages", StaticFiles(directory=pages_dir), "pages")


# Spawn instance of proxy
@app.post("/proxy/new/{config_id}", tags=["Proxies"])
async def new_proxy(config_id: int) -> int:
    db = DB()

    try:
        config = db.get_config(config_id)
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    return await proxy_manager.new(config)


# Delete an instance of a proxy
@app.delete("/proxy/{proxy_id}", tags=["Proxies"])
async def terminate_proxy(proxy_id: int):
    try:
        proxy_manager.terminate(proxy_id)
    except ProxyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


# Create a new config
@app.post("/config/new", tags=["Configs"])
async def new_config(config: Config) -> int:
    db = DB()
    return db.new_config(config)


# Get all configs
@app.get("/config/all", tags=["Configs"])
async def get_configs() -> Configs:
    db = DB()
    
    configs = db.get_configs()
    if not configs:
        raise HTTPException(status_code=404, detail="No configs found")

    return configs


# Get full config
@app.get("/config/{config_id}", tags=["Configs"])
async def get_config(config_id: int) -> Config:
    db = DB()

    try:
        config = db.get_config(config_id)
        return config
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    

# Delete a config
@app.delete("/config/{config_id}", tags=["Configs"])
async def delete_config(config_id: int):
    db = DB()
    
    try:
        db.delete_config(config_id)
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.put("/config/{config_id}", tags=["Configs"])
async def update_config(config_id: int, config: Config):
    db = DB()

    try:
        db.update_config(config_id, config)
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


# Clean up proxies on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before shutdown
    yield
    # During shutdown
    proxy_manager.cleanup()
