import socket
import threading
import time
import logging
from socketserver import BaseRequestHandler

from db import DB
from models import Config
from src.db_exceptions import BlacklistingWhitelistedException

config_id: int | None = None
config: Config | None = None
db = DB()



# In-memory storage for IP request tracking and blocks
request_counts = {}
lock = threading.Lock()
BLOCK_DURATION = 60  # seconds

class RequestHandler(BaseRequestHandler):
    def handle(self):
        assert config and config_id

        client_ip = self.client_address[0]

        # Check if IP is blocked
        with lock:
            if db.is_in_blacklist(config_id, client_ip):
                logging.warning(f"Blocked request from {client_ip}")
                return

        # Rate limiting
        now = time.time()
        with lock:
            history = request_counts.get(client_ip, [])
            history = [t for t in history if now - t < 1]
            history.append(now)
            request_counts[client_ip] = history

            if config.max_requests_per_second and len(history) > config.max_requests_per_second:
                logging.warning(f"Too many requests from {client_ip}. Temporarily blocked.")
                try:
                    db.add_to_blacklist(config_id, client_ip)
                except BlacklistingWhitelistedException as e:
                    logging.error(str(e))
                return

        logging.info(f"Request from {client_ip}")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((config.real_host, config.real_port))

            in_thread = threading.Thread(target=self.forward, args=(self.request, self.sock))
            out_thread = threading.Thread(target=self.forward, args=(self.sock, self.request))

            in_thread.start()
            out_thread.start()

            in_thread.join()
            out_thread.join()
        except Exception as e:
            logging.error(f"Error handling request from {client_ip}: {e}")

    def forward(self, in_sock, out_sock):
        assert config and config_id

        n_bytes = 0
        while not config.max_bytes_per_request or n_bytes < config.max_bytes_per_request:
            chunk = in_sock.recv(4096)
            if not chunk:
                break
            out_sock.send(chunk)
            n_bytes += len(chunk)
