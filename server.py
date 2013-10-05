import sqlite3, settings, socket, SimpleHTTPServer, SocketServer, threading, time, json, re
import iotest

class ModHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    bpmServer = None
    
    def do_GET(self):
        if re.match(r"/cmd\.json", self.path):
            parts = self.path.split("?")
            if len(parts) == 2:
                msg = json.dumps(self.bpmServer.handleCMD(parts[1]))
            else: 
                msg = "Error! wrong number of args!"
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
        else:
            self.path = "/www" + self.path
            f = self.send_head()
            if f:
                self.copyfile(f, self.wfile)
                f.close()

class HTTPserver(threading.Thread):
    
    port = 8080
    
    bpmServer = None
    
    def run(self):
        Handler = ModHTTPRequestHandler
        
        Handler.bpmServer = self.bpmServer
    
        httpd = SocketServer.TCPServer(("", self.port), Handler)
    
        print "HTTP> Serving at port", self.port
        httpd.serve_forever()
        
class BPMServer():
    
    db = sqlite3.connect("music.sqlite")

    c = db.cursor()
    diff = settings.conf["max_diff"]
    
    server = HTTPserver()
    
    played = []
    
    last_tick = time.time()
    bpmHistory = [0] * settings.conf["average"]
    bpmAverage = 0
    bpm = 0
    
    info = {
        "bpm": 0,
        "song": {
                "title": "Songname", 
                "artist": "Songartist", 
                "length": 325,
                "bpm":-1
                },
        "pos": 125
        }
    
    def run(self):
        
        print("HTTP> Starting HTTP Server!")
        
        self.server.daemon = True
        self.server.bpmServer = self
        self.server.start()
        
        iotest.start(self)
        
        while True:
            
            #print("Run> Current BPM is %s" % )
            if self.bpm != 0 and time.time()-self.last_tick>settings.conf["timeout"]:
                self.bpm = 0
            del self.bpmHistory[0]
            self.bpmHistory.append(self.bpm)
<<<<<<< HEAD
            self.bpmAverage = (sum(self.bpmHistory)/settings.conf["average"])        #see TODO: Add mechanism to change the length in the config File  
            print("Run> BPM Statistics: Current BPM is %.2f - Average BPM is %.2f - Difference is %.2f" % (self.bpm,self.bpmAverage, time.time() - self.last_tick) )
=======
            self.bpmAverage = (sum(self.bpmHistory) / settings.conf["average"])  
            print("Run> BPM Statistics: Current BPM is %s - Average BPM is %s - Difference is %s" % (self.bpm,self.bpmAverage, time.time() - self.last_tick) )
>>>>>>> branch 'master' of https://github.com/Phythm/Phythm.git
            

            time.sleep(1)
        
    def bpmTick(self):
        curr = time.time()
        diff = curr - self.last_tick
        self.last_tick = curr
        self.bpm = (1.0 / diff) * 60.0
        print("BPM> update to %s" % self.bpm)

        
        #print("Tick! " + str(diff))
        
    def handleCMD(self, cmd):
        print("HTTP> Handling:" + cmd)
        if cmd.lower() == "info":
            return {"status": 0, "message": self.info}
        else:
            return {"status": -1, "message": "Error: command " + cmd + " not found"}
    
    def getBestMatch(bpm):
        global played
        c.execute('SELECT * FROM "music" WHERE "bpm" >= ? AND "bpm" <= ? ORDER BY ABS("bpm" - ?) ASC;', (bpm - diff, bpm + diff, bpm))
        for song in c:
            if song[0] in played:
                continue
            played += [song[0]]
            return song[2]
        played = []
        return getBestMatch(bpm)
        


BPMServer().run()
#s = socket.socket()

#s.bind(("", 8000))

#s.listen(1)

#conn, addr = s.accept()

#print(addr)

#db.commit()
