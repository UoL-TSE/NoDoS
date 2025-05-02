import uvicorn

from config import config


def run_admin_panel(debug=False):
    # Arguments if debug move is specified
    debug_args = {
        "reload": True,
        "log_level": "debug"
    } if debug else {}

    # Run FastAPI app
    uvicorn.run(
        "admin.app:app",
        host=config.admin_host,
        port=config.admin_port,
        **debug_args
    )
