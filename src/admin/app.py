from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles

from proxy_manager import ProxyNotFound, proxy_manager
from db import DB
from models import *
from db_exceptions import ConfigNotFoundException, UsernameTakenException
from .auth import auth_handler


# Initialize app
app = FastAPI()

# Serve pages directory as a static site
admin_dir = Path(__file__).parent.absolute()
pages_dir = f"{admin_dir}/pages"
app.mount("/pages", StaticFiles(directory=pages_dir), "pages")


@app.post('/auth/register', status_code=201, tags=["Auth"])
def register(auth_details: AuthDetails) -> None:
    if not (auth_details.username.endswith('@students.lincoln.ac.uk') or auth_details.username.endswith('@lincoln.ac.uk')):
        raise HTTPException(status_code=400, detail='Username must end with @students.lincoln.ac.uk or @lincoln.ac.uk')

    db = DB()
    try:
        db.register_user(auth_details)
    except UsernameTakenException as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post('/auth/login', tags=["Auth"])
def login(auth_details: AuthDetails) -> Token:
    db = DB()
    cursor = db.conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE name = %s", (auth_details.username,))

    result = cursor.fetchone()
    if not result:
        raise HTTPException(status_code=401, detail='Invalid username or password')

    user_id, hashed_password = result
    if not auth_handler.verify_password(auth_details.password, hashed_password):
        raise HTTPException(status_code=401, detail='Invalid username or password')

    token = auth_handler.encode_token(user_id)
    return Token(token=token)


# Delete a user from the database
@app.delete('/auth', tags=["Auth"])
def delete_user(user_id: int = Depends(auth_handler.auth_wrapper)) -> None:
    db = DB()
    db.delete_user(user_id)


# Spawn instance of proxy
@app.post("/proxy/new/{config_id}", tags=["Proxies"])
async def new_proxy(config_id: int, user_id: int = Depends(auth_handler.auth_wrapper)) -> ProxyID:
    db = DB()

    try:
        config = db.get_config(user_id, config_id)
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    proxy_id = await proxy_manager.new(user_id, config_id, config)
    return ProxyID(proxy_id=proxy_id)


# Delete an instance of a proxy
@app.delete("/proxy/{proxy_id}", tags=["Proxies"])
async def terminate_proxy(proxy_id: int, user_id: int = Depends(auth_handler.auth_wrapper)):
    try:
        proxy_manager.terminate(proxy_id)
    except ProxyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    

# Get all proxies that are running
@app.get("/proxy/all", tags=["Proxies"])
async def all_proxies(user_id: int = Depends(auth_handler.auth_wrapper)) -> Proxies:
    proxies = proxy_manager.allproxies()

    if not proxies:
        raise HTTPException(status_code=404, detail="No proxies running")

    return Proxies(
        proxies=[
            Proxy(
                proxy_id=i,
                running=proxy.process.is_alive(),
                exit_code=proxy.exit_code,
                error_message=proxy.error_message,
                config=proxy.config
            )
            for i, proxy in enumerate(proxies) if proxy
        ]
    )


# Create a new config
@app.post("/config/new", tags=["Configs"])
async def new_config(config: Config, user_id: int = Depends(auth_handler.auth_wrapper)) -> ConfigID:
    db = DB()
    config_id = db.new_config(user_id, config)
    return ConfigID(config_id=config_id)


# Get all configs
@app.get("/config/all", tags=["Configs"])
async def get_configs(user_id: int = Depends(auth_handler.auth_wrapper)) -> Configs:
    db = DB()
    
    configs = db.get_configs(user_id)
    if not configs:
        raise HTTPException(status_code=404, detail="No configs found")

    return configs


# Get full config
@app.get("/config/{config_id}", tags=["Configs"])
async def get_config(config_id: int, user_id: int = Depends(auth_handler.auth_wrapper)) -> Config:
    db = DB()

    try:
        config = db.get_config(user_id, config_id)
        return config
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    

# Delete a config
@app.delete("/config/{config_id}", tags=["Configs"])
async def delete_config(config_id: int, user_id: int = Depends(auth_handler.auth_wrapper)):
    db = DB()
    
    try:
        db.delete_config(user_id, config_id)
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
@app.put("/config/{config_id}", tags=["Configs"])
async def update_config(config_id: int, config: Config, user_id: int = Depends(auth_handler.auth_wrapper)):
    db = DB()

    try:
        db.update_config(user_id, config_id, config)
    except ConfigNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


# Clean up proxies on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Before shutdown
    yield
    # During shutdown
    proxy_manager.cleanup()
