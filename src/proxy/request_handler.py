import socket
import threading
import time
import logging
from socketserver import BaseRequestHandler

from models import Config

config: Config | None = None

# Setup logging
logging.basicConfig(filename='dos_protection.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for IP request tracking and blocks
request_counts = {}
blocked_ips = {}
lock = threading.Lock()
BLOCK_DURATION = 60  # seconds

class RequestHandler(BaseRequestHandler):
    def handle(self):
        assert config

        client_ip = self.client_address[0]

        # Check if IP is blocked
        with lock:
            if client_ip in blocked_ips:
                if time.time() < blocked_ips[client_ip]:
                    logging.warning(f"Blocked request from {client_ip}")
                    return
                else:
                    del blocked_ips[client_ip]

        # Rate limiting
        now = time.time()
        with lock:
            history = request_counts.get(client_ip, [])
            history = [t for t in history if now - t < 1]
            history.append(now)
            request_counts[client_ip] = history

            if config.max_requests_per_second and len(history) > config.max_requests_per_second:
                logging.warning(f"Too many requests from {client_ip}. Temporarily blocked.")
                blocked_ips[client_ip] = now + BLOCK_DURATION
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
        assert config

        n_bytes = 0
        while not config.max_bytes_per_request or n_bytes < config.max_bytes_per_request:
            chunk = in_sock.recv(4096)
            if not chunk:
                break
            out_sock.send(chunk)
            n_bytes += len(chunk)
