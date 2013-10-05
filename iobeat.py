import socket, time, random

print("Sending 1 beat-byte")

s = socket.socket()
    #s.bind(("", 8000))
s.connect(("localhost", 8000))

while True:
    
    s.sendall("t")
    raw_input()



