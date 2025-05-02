from config import config
from request_handler import RequestHandler
from tcp_server import TCPServer

if __name__ == "__main__":
    print(f"Running on {config.host}:{config.port}")
    print(f"Forwarding for {config.real_host}:{config.real_port}")
    
    # Initialise TCPServer
    with TCPServer((config.host, config.port), RequestHandler) as server:
        server.serve_forever()
