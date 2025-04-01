import os
from socketserver import ForkingMixIn, TCPServer as _TCPServer, ThreadingMixIn

"""
If running on Windows, use the threading mixin as the
Windows kernel is optimised for threading rather than forking
"""
if os.name == "nt":
    MixIn = ThreadingMixIn
else:
    MixIn = ForkingMixIn


class TCPServer(MixIn, _TCPServer):
    pass
