import os
import socketserver
import socketserver


"""
If running on Windows, use the threading mixin as the
Windows kernel is optimised for threading rather than forking
"""
if os.name == "nt":
    MixIn = socketserver.ThreadingMixIn
else:
    MixIn = socketserver.ForkingMixIn


class TCPServer(MixIn, socketserver.TCPServer):
    pass
