import logging
from multiprocessing import Pipe, Process
from multiprocessing.connection import Connection
from typing import Any

from models import Config
import proxy.request_handler as rh
from .tcp_server import TCPServer


def _run_proxy(config_id: int, config: Config, conn: Connection):
    rh.config_id = config_id
    rh.config = config
    
    # Setup logging
    logging.basicConfig(filename=f'logs/dos_protection_{config_id}.log', level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # Initialise TCPServer
    server: TCPServer | None
    exit_code = 0
    try:
        server = TCPServer((config.proxy_host, config.proxy_port), rh.RequestHandler)
        print(f"Running proxy on {config.proxy_host}:{config.proxy_port}",
              f"Forwarding for {config.real_host}:{config.real_port}",
              sep="\n")

        server.serve_forever()
    except Exception as e:
        conn.send(str(e))

        if isinstance(e, OSError):
            exit_code = e.errno
    finally:
        conn.close()
        exit(exit_code)


class Proxy:
    user_id: int
    config_id: int

    process: Process
    proc_conn: Connection
    exit_code: int | None = None
    error_message: str | None = None

    def __init__(self, user_id: int, config_id: int, config: Config):
        self.proc_conn, child_conn = Pipe()
        self.user_id = user_id
        self.config_id = config_id
        
        self.process = Process(target=_run_proxy, args=(config_id, config, child_conn))
        self.process.start()

    def poll(self):
        if self.exit_code is not None:
            return

        self.exit_code = self.process.exitcode
        if self.exit_code is None:
            return

        self.process.join()
        if self.proc_conn.poll():
            self.error_message = self.proc_conn.recv()

    def terminate(self):
        self.process.terminate()
        self.process.join()
        self.process.close()
