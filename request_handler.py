from socketserver import StreamRequestHandler


# Class for handling requests
# Inherits from StreamRequestHandler
class RequestHandler(StreamRequestHandler):
    def handle(self):
        # self.rfile: File like object to handle recieving data
        # self.wfile: File like object to handle response

        # Store recieved bytes
        self.data = self.rfile.readline(10000).rstrip()
        
        # Print recieved data as a utf-8 string
        print(f"{self.client_address[0]} wrote:")
        print(self.data.decode("utf-8"))

        # Respond with received message in uppercase
        self.wfile.write(self.data.upper())
