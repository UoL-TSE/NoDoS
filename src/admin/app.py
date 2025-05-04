from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles

from proxy_manager import ProxyNotFound, proxy_manager
from db import DB
from models import *
from db_exceptions import ConfigNotFoundException
from .auth import AuthHandler


# Initialize app
app = FastAPI()

# Serve pages directory as a static site
admin_dir = Path(__file__).parent.absolute()
pages_dir = f"{admin_dir}/pages"
app.mount("/pages", StaticFiles(directory=pages_dir), "pages")


auth_handler = AuthHandler()
users = []


@app.post('/register', status_code=201, tags=["Auth"])
def register(auth_details: AuthDetails):
    if any(x['username'] == auth_details.username for x in users):
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = auth_handler.get_password_hash(auth_details.password)
    users.append({
        'username': auth_details.username,
        'password': hashed_password    
    })
    return {"Reigistered!": auth_details.username}


@app.post('/login', tags=["Auth"])
def login(auth_details: AuthDetails):
    user = None
    for x in users:
        if x['username'] == auth_details.username:
            user = x
            break
    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user['username'])
    return { 'token': token }


# Spawn instance of proxy
@app.post("/proxy/new/{config_id}", tags=["Proxies"])
async def new_proxy(config_id: int, username: str = Depends(auth_handler.auth_wrapper)) -> ProxyID:
    db = DB()

    try:
        config = db.get_config(config_id)
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    proxy_id = await proxy_manager.new(config)
    return ProxyID(proxy_id=proxy_id)


# Delete an instance of a proxy
@app.delete("/proxy/{proxy_id}", tags=["Proxies"])
async def terminate_proxy(proxy_id: int, username: str = Depends(auth_handler.auth_wrapper)):
    try:
        proxy_manager.terminate(proxy_id)
    except ProxyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    

# Get all proxies that are running
@app.get("/proxy/all", tags=["Proxies"])
async def all_proxies(username: str = Depends(auth_handler.auth_wrapper)) -> Proxies:
    # Get all proxies that are running
    proxies = proxy_manager.allproxies()

    if not proxies:
        raise HTTPException(status_code=404, detail="No proxies running")

    return Proxies(
        proxies=[
            {
                "Proxy ID": i,
                "Status": proxy.is_alive(),
                "Exit Code": proxy.exitcode
            } for i, proxy in enumerate(proxies)
        ]
    )
    

# Create a new config
@app.post("/config/new", tags=["Configs"])
async def new_config(config: Config, username: str = Depends(auth_handler.auth_wrapper)) -> ConfigID:
    db = DB()
    config_id = db.new_config(config)
    return ConfigID(config_id=config_id)


# Get all configs
@app.get("/config/all", tags=["Configs"])
async def get_configs(username: str = Depends(auth_handler.auth_wrapper)) -> Configs:
    db = DB()
    
    configs = db.get_configs()
    if not configs:
        raise HTTPException(status_code=404, detail="No configs found")

    return configs


# Get full config
@app.get("/config/{config_id}", tags=["Configs"])
async def get_config(config_id: int, username: str = Depends(auth_handler.auth_wrapper)) -> Config:
    db = DB()

    try:
        config = db.get_config(config_id)
        return config
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    

# Delete a config
@app.delete("/config/{config_id}", tags=["Configs"])
async def delete_config(config_id: int, username: str = Depends(auth_handler.auth_wrapper)):
    db = DB()
    
    try:
        db.delete_config(config_id)
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.put("/config/{config_id}", tags=["Configs"])
async def update_config(config_id: int, config: Config, username: str = Depends(auth_handler.auth_wrapper)):
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
