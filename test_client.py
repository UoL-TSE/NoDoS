import socket
import sys

HOST, PORT = "localhost", 8080
data = " ".join(sys.argv[1:])

# Create TCP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server
    sock.connect((HOST, PORT))

    # Send data
    sock.sendall(bytes(data, "utf-8"))
    sock.sendall(b"\n")

    # Receive data from the server and shut down
    received = str(sock.recv(1024), "utf-8")

print("Sent:    ", data)
print("Received:", received)
