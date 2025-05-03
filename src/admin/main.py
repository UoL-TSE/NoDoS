import os
import uvicorn

from config import config


# Fix permission denied bug when using watchfiles (for debug reloading)
os.environ["WATCHFILES_IGNORE_PERMISSION_DENIED"] = "true";

def run_admin_panel(debug=False):
    # Arguments if debug move is specified
    debug_args = {
        "reload": True,
        "log_level": "debug",
        "reload_dirs": "/home/callum/Documents/Programming/Python/NoDoS/src",
    } if debug else {}

    # Run FastAPI app
    uvicorn.run(
        "admin.app:app",
        host=config.admin_host,
        port=config.admin_port,
        **debug_args
    )
