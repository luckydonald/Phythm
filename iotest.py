import threading, socket

class serverThread(threading.Thread):
    
    bpmServer = None
    
    def run(self):
        s = socket.socket()
        s.bind(("", 8000))
        s.listen(1)
        conn, addr = s.accept()
        conn.setblocking(True)
        while True:
            conn.recv(1)
            self.bpmServer.bpmTick()

def start(bpmServer):
    s = serverThread()
    s.deamon = True
    s.bpmServer = bpmServer
    s.start()

