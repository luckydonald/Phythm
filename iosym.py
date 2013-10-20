import socket, time, random

#print("Start")
print("BPM:")
bpm = int(raw_input())
print("Random spread:")
diff = int(raw_input())

s = socket.socket()
    #s.bind(("", 8000))
s.connect(("localhost", 8000))
try:
    
    while True:
        
        s.sendall("t")
        bpm_to_use = bpm + random.randint(-diff/2, diff/2)
        print("Simulating BPM:%i" % bpm_to_use)
        time.sleep((1.0 / (bpm_to_use)) * 60.0)
        #print("tick")
except KeyboardInterrupt:
    s.close()
    print("shut down.")