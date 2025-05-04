import os
import uvicorn


# Fix permission denied bug when using watchfiles (for debug reloading)
os.environ["WATCHFILES_IGNORE_PERMISSION_DENIED"] = "true";

def run_admin_panel(port: int=8080, debug=False):
    # Arguments if debug move is specified
    debug_args = {
        "reload": True,
        "log_level": "debug",
        "reload_dirs": "/home/callum/Documents/Programming/Python/NoDoS/src",
    } if debug else {}

    # Run FastAPI app
    uvicorn.run(
        "admin.app:app",
        host="127.0.0.1",
        port=port,
        **debug_args
    )
