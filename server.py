#!/usr/bin/env python
import json, random, re, sqlite3, settings, string, socket, SimpleHTTPServer, SocketServer, threading, time
import signal
import eyed3, iotest, moc
 # as seen in https://github.com/jonashaag/python-moc   -  DOC at http://moc.lophus.org/



class ModHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    bpmServer = None
    
    def do_GET(self):
        if re.match(r"/cmd\.json", self.path):
            parts = self.path.split("?")
            if len(parts) == 2:
                msg = json.dumps(self.bpmServer.handleCMD(parts[1]), sort_keys=True, indent=4, separators=(',', ': '))
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
    
    port = settings.conf["port"]
    
    bpmServer = None
    
    def run(self):
        Handler = ModHTTPRequestHandler
        
        Handler.bpmServer = self.bpmServer
    
        httpd = SocketServer.TCPServer(("", self.port), Handler)
    
        print "HTTP> Serving at port", self.port
        httpd.serve_forever()
        
class BPMServer():
    def stringGenerator(self,length):
        return ''.join(random.choice(string.lowercase) for i in range(length))
    
    diff = settings.conf["max_diff"]
    
    server = HTTPserver()
    
    playing_index = 0
    played_history = []
    
    last_tick = time.time()
    bpmHistory = [0] * settings.conf["average"]
    bpmAverage = 0
    bpm = 0
    keep_running = True
    
    shutdownCommand = "0000" #default, overwritten later.
    info = {
        "bpm": 0,
        "song": {
                "title": "Songname",
                "album": "Songalbum", 
                "artist": "Songartist", 
                "currentsec": 325,
                "totalsec": 125,
                "bpm":-1,
                "file": "/music/songname.mp3",
                "playingstate": 2 #playing state ( 0=stopped; 1=paused; 2=playing )
                },
        "history": {
                   },
        "history_index": 0  
        }
    
    def run(self):
        
        print("HTTP> Starting HTTP Server!")

        self.server.daemon = True
        self.server.bpmServer = self
        self.server.start()
        
        iotest.start(self)
        self.shutdownCommand = self.stringGenerator(6)  #shutdown via webUI
        print("To Shut down please visit http://localhost:%s/cmd.json?%s via your Browser." % (settings.conf["port"],self.shutdownCommand))
        while (self.keep_running == True):
            
            if self.bpm != 0 and time.time()-self.last_tick>settings.conf["timeout"]:
                self.bpm = 0
            del self.bpmHistory[0]
            self.bpmHistory.append(self.bpm)
            self.bpmAverage = (sum(self.bpmHistory)/settings.conf["average"])
            self.info["bpm"] = self.bpmAverage 
            #print("Run> %s BPM Statistics: Current BPM is %03.2f - Average BPM is %03.2f - Difference is %03.2f" % (self.keep_running, self.bpm,self.bpmAverage, time.time() - self.last_tick))
            
            time.sleep(1)
        
    def bpmTick(self):
        curr = time.time()
        diff = curr - self.last_tick
        self.last_tick = curr
        self.bpm = (1.0 / diff) * 60.0
        #print("BPM> update to %s" % self.bpm)

        
        #print("Tick! " + str(diff))
        
    def handleCMD(self, cmd):
        #print("HTTP> Handling:" + cmd)
        if cmd.lower() == "info":
            self.updatePlayerStatisInfo()
            return {"status": 0, "message": self.info}
        
        if cmd.lower() == "playlast":
            print(self.played_history)
            self.playing_index +=  -1
            print("CMD> %i Last Old Song: %s" % (self.playing_index, self.played_history[self.playing_index][2]))
            self.playSong(self.played_history[self.playing_index][2])
            self.updatePlayerStatisInfo()
            return {"status": 0, "message": self.info}
            
        if cmd.lower() == "playnext":
            print(self.played_history)
            self.playing_index += +1
            if(self.playing_index == len(self.played_history)):
                songToPlay = self.getBestMatch(self.bpmAverage,self.diff) #should add new song AND jump to new song
            print("CMD> %i Next Old Song: %s" % (self.playing_index, self.played_history[self.playing_index][2]))
            self.playSong(self.played_history[self.playing_index][2])
            self.updatePlayerStatisInfo()
            return {"status": 0, "message": self.info} 
          
        if cmd.lower() == "forcenext":
            songToPlay = self.getBestMatch(self.bpmAverage,self.diff)
            print("CMD> %i New Song: %s" % (self.playing_index, songToPlay[2]))
            self.playSong(songToPlay[2])
            self.updatePlayerStatisInfo()
            return {"status": 0, "message": self.info}
            
        if cmd.lower() == "playpause":
            songToPlay = self.getBestMatch(self.bpmAverage,self.diff)
            if moc.is_playing():
                moc.pause()
            else:
                moc.unpause()
            self.updatePlayerStatisInfo()
            print("CMD> updated self.info")
            print(self.info)
            return {"status": 0, "message": self.info}
        
        
            
            
        if cmd.lower() == self.shutdownCommand:
            self.softQuit();
        else:
            return {"status": -1, "message": "Error: command " + cmd + " not found"}
    
    def getBestMatch(self,bpm,diff):
        db = sqlite3.connect("music.db") #changed extention
        c = db.cursor()
        c.execute('SELECT * FROM "music" WHERE "bpm" >= ? AND "bpm" <= ? ORDER BY ABS("bpm" - ?) ASC;', (bpm - diff, bpm + diff, bpm)) #TODO bpm / 2, bpm * 2 
        for song in c: 
                            # (index, bpm, file)  #index starts at 1!
                            # (1, -1, u'/music/SUBFOLDER/(I Want to Wear) Yellow & Blue - TalkAcanthi - Rocking is Magic.mp3')

            print("Match> Song is %s" % song[2])
            print(song)
            if song in self.played_history:
                print("Match> Already played, skipping.")
                continue
            self.played_history.append(song)
            self.playing_index=len(self.played_history)-1 #Reset 
            return song #stop here            
            
        db.close()
        return self.getBestMatch(bpm,diff+5)
        
    def playSong(self,file):
        songInfo = moc.quickplay([file])
        
        return songInfo
    
    def getPlayerStatus(self):
        songInfo = moc.info()
        #print("getPlyrStats> moc.info() returns")
        #print(songInfo)
        if songInfo['state']==0:
            parsedInfo = {
                "title": "-",
                "album": "-", 
                "artist": "-", 
                "currentsec": 0,
                "totalsec": 0,
                "bpm":0,
                "file": "",
                "playingstate": 0 #playing state
                }
        else:
            audiofile = eyed3.load(songInfo['file'])
            bpm = audiofile.tag.bpm
            parsedInfo = {
                "title": songInfo['songtitle'],
                "album": songInfo['album'], 
                "artist": songInfo['artist'], 
                "currentsec": songInfo['currentsec'],
                "totalsec": songInfo['totalsec'],
                "bpm":bpm,
                "file": songInfo['file'],
                "playingstate": songInfo['state'] #playing state
                }   
        return parsedInfo
    
    def updatePlayerStatisInfo(self):
        self.info["song"] = self.getPlayerStatus()
        self.info["history"] = self.played_history #[id,bpm,path]
        self.info["history_index"] = self.playing_index


    def softQuit(self):
        print("=== Shutting down ===")
        try:
            moc.stop()
            print("DOWN> stopping moc server.")
            moc.stop_server()
        except MocNotRunning:
            print("DOWN> already stopped moc server.")  
        keep_running = False
        print("=== Shutting down ===")

        #TODO: insert boolean 'running' in while true, so it is nice and neat.

"""
def handler(signum, frame):
    print "Forever is over!"
    raise Exception("end of time")

def start_server():
    print("INIT> starting moc server.")
    try:      
        moc.start_server()
    except moc.MocError:
        print("INIT> moc server already running.") 
        signal.alarm(0)

signal.signal(signal.SIGALRM, handler)
signal.alarm(10)
try:
    start_server()
except Exception, exc: 
    print exc

#handler(None,None)
signal.alarm(0)
"""

print("INIT> starting bmp server.")  
BPMServer().run()
print("INIT> started both servers.")
#keep_running = True    
  

