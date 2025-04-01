import request_handler as rh
from tcp_server import TCPServer

if __name__ == "__main__":
    # Define host and port of proxy
    HOST, PORT = "localhost", 8080

    # Initialise TCPServer
    with TCPServer((HOST, PORT), rh.RequestHandler) as server:
        server.serve_forever()
