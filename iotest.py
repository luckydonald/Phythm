import threading, time, socket

class serverThread(threading.Thread):
    
    bpmServer = None
    
    def run(self):
        s = socket.socket()
        failed=True
        while failed:
            print("BPM SERVER> Setting Port 8000")
            try:
                s.bind(("", 8000))
                failed = False
            except:
                print("BPM SERVER> Aaaand you failed.")
                time.sleep(1)
                
                
        #blarg
             

        while True:
            try:    
                s.listen(5)
                conn, addr = s.accept()
                #conn.setblocking(True)
                while True:
                    conn.recv(1)
                    self.bpmServer.bpmTick()
            except Exception as inst:
                print type(inst)     # the exception instance
                print inst.args      # arguments stored in .args
                print inst
                s.close()
                time.sleep(1)
                print("BPM SERVER> Restarting...") 

def start(bpmServer):
    s = serverThread()
    s.deamon = True
    s.bpmServer = bpmServer
    s.start()

