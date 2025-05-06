import socketserver


MixIn = socketserver.ThreadingMixIn
class TCPServer(MixIn, socketserver.TCPServer):
    pass
