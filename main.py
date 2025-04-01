import request_handler as rh
from socketserver import TCPServer

if __name__ == "__main__":
    # Define host and port of proxy
    HOST, PORT = "localhost", 8080

    # TODO: Write custom TCPServer implementation
    # Initialise TCPServer
    with TCPServer((HOST, PORT), rh.RequestHandler) as server:
        server.serve_forever()
