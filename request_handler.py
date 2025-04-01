import socket
import threading
from socketserver import BaseRequestHandler
from config import config

# Class for handling requests
# Inherits from BaseRequestHandler
class RequestHandler(BaseRequestHandler):
    def handle(self):
        # self.rfile: File like object to handle recieving data
        # self.wfile: File like object to handle response
        
        print(f"Request from {self.client_address}")

        # Connect to underlying server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((config.real_host, config.real_port))

        # Initialize threads for both forwarding to the server and the client
        in_thread = threading.Thread(target=self.forward, args=(self.request, self.sock))
        out_thread = threading.Thread(target=self.forward, args=(self.sock, self.request))

        # Start the threads
        in_thread.start()
        out_thread.start()

        # Join (wait for completion) the threads
        in_thread.join()
        out_thread.join()

    def forward(self, in_sock, out_sock):
        # Store recieved bytes
        n_bytes: int = 0

        # While the bytes transferred are less than the maximum allowed per request
        while n_bytes < config.max_bytes_per_request:
            chunk = in_sock.recv(4096) 
            out_sock.send(chunk)
            
            # If an empty chunk is found, end of transmission
            if chunk == b'':
                break
            
            # Count length of new chunk
            n_bytes += len(chunk)
