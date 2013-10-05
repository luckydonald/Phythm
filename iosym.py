import socket, time, random

#print("Start")

s = socket.socket()
    #s.bind(("", 8000))
s.connect(("localhost", 8000))

while True:
    
    s.sendall("t")
    
    time.sleep((1.0 / (120 + random.randint(-10, 10))) * 60.0)
    #print("tick")
