#!/usr/bin/env python
import json, random, re, sqlite3, settings, string, socket, SimpleHTTPServer, SocketServer, threading
import iotest, time, math #bpm
import eyed3, moc #id3 and the player
from mutagen import File #cover artwork
#from PIL import Image #better cover artwork processing.
import io #better cover artwork processing.
from StringIO import StringIO
import module_locator
import base64 #cover artwork
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
            return
        if re.match(r"(.*?)/(cover.png)", self.path):
            msg = self.bpmServer.cover_data
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return
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
    
    autoplaynext_enabled = True
    autoplaynext_endtime = time.time()
    www_path = module_locator.module_path() + "/www/" #get
    print("Webdir> %s" % www_path)

    cover_data = "";
    #cover_small = "";
    last_tick =  time.time(); #hui
    last_file =  ""
    bpmHistory = [160] * settings.conf["average"]
    bpmAverage = 0
    bpm = 0
    bpmShift = 0  #pitch via Web UI
    keep_running = True
    debug = False
    shutdownCommand = "0000" #default, overwritten later.
    info = {
        "bpm": 0,
        "bpmShift":+0,
        "song": {
                "id": -2,
                "title": "Songname",
                "album": "Songalbum", 
                "artist": "Songartist", 
                "currentsec": 325,
                "totalsec": 125,
                "bpm":-1,
                "file": "/music/songname.mp3",
                "playingstate": 2, #playing state ( 0=stopped; 1=paused; 2=playing )
                "cover":""
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
        for _ in range(5):
            print("To Shut down please visit http://localhost:%s/cmd.json?%s via your Browser." % (settings.conf["port"],self.shutdownCommand))
        while (self.keep_running == True):
            #del self.bpmHistory[0]
            #self.bpmHistory.append(self.bpm)
            if self.bpm != 0 and time.time()-self.last_tick>settings.conf["timeout"]:
                self.bpm = 0
            del self.bpmHistory[0]
            self.bpmHistory.append(self.bpm)
            self.bpmAverage = (sum(self.bpmHistory)/settings.conf["average"]) 
            self.info["bpm"] = self.bpmAverage + self.bpmShift
            #print (self.autoplaynext_enabled, " | ", self.autoplaynext_endtime, "<",  time.time(), " = ", self.autoplaynext_endtime-time.time())
            if self.autoplaynext_enabled and self.autoplaynext_endtime < time.time():
                #self.autoplaynext_enabled = False
                songToPlay = self.getBestMatch(self.bpm + self.bpmShift,self.diff)
                print("Main> %i New Song: %s" % (self.playing_index, songToPlay[2]))
                self.playSong(songToPlay[2])  
                self.updatePlayerStatisInfo()
            
            #print("Run> %s BPM Statistics: Current BPM is %03.2f - Average BPM is %03.2f - Difference is %03.2f" % (self.keep_running, self.bpm,self.bpmAverage, time.time() - self.last_tick))
            time.sleep(1) #important for CPU usage.
        
    def bpmTick(self): #DO NOT CALL THIS FROM THIS MAIN THREAD!!!!
        curr = time.time() #now
        diff = curr - self.last_tick
        self.last_tick = curr
        self.bpm = ((1.0 / diff) * 60.0 ) + self.bpmShift
             
        #print("Tick! " + str(diff))
        
    def handleCMD(self, cmd): #DO NOT CALL THIS FROM THIS MAIN THREAD!!!! NEVER!
        #print("HTTP> Handling:" + cmd)
        if cmd.lower() == "info":
            self.updatePlayerStatisInfo()
            return {"status": 2, "info": self.info}
        
        if cmd.lower() == "playlast":
            print(self.played_history)
            self.playing_index +=  -1
            print("CMD> %i Last Old Song: %s" % (self.playing_index, self.played_history[self.playing_index]["path"]))
            self.playSong(self.played_history[self.playing_index]["path"])
            self.updatePlayerStatisInfo()
            return {"status": 102, "info": self.info}
        
        if cmd.lower().startswith('play&id='):
            rg = re.compile('(play&id=)'+'(\\d+)',re.IGNORECASE|re.DOTALL)
            m = rg.search(cmd.lower())
            if m:
                print(m)
                self.playing_index = index=int(m.group(2))
                
                print("CMD> %i Last Old Song: %s" % (self.playing_index, self.played_history[self.playing_index]["path"]))
                self.playSong(self.played_history[self.playing_index]["path"])
                self.updatePlayerStatisInfo()
                return {"status": 102, "info": self.info}
            return {"status": -102, "error": "Error in Regular Expression. Int (\\d+) not found."}
        
        
        if cmd.lower() == "playnext":
            print(self.played_history)
            self.playing_index += +1
            if(self.playing_index == len(self.played_history)):
                songToPlay = self.getBestMatch(self.bpm + self.bpmShift,self.diff) #should add new song AND jump to new song
            print("CMD> %i Next Old Song: %s" % (self.playing_index, self.played_history[self.playing_index]["path"]))
            self.playSong(self.played_history[self.playing_index]["path"])
            self.updatePlayerStatisInfo()
            return {"status": 102, "info": self.info} 
          
        if cmd.lower() == "forcenext":
            songToPlay = self.getBestMatch(self.bpm + self.bpmShift,self.diff)
            print("CMD> %i New Song: %s" % (self.playing_index, songToPlay[2]))
            self.playSong(songToPlay[2])
            self.updatePlayerStatisInfo()
            return {"status": 0, "info": self.info}
            
        if cmd.lower() == "playpause":
            #songToPlay = self.getBestMatch(self.bpm + self.bpmShift,self.diff)
            if moc.is_playing():
                self.pauseSong()
            else:
                self.resumeSong()
                
            self.updatePlayerStatisInfo()
            print("CMD> updated self.info")
            print(self.info)
            return {"status": 102, "info": self.info}
        
        if cmd.lower() == "fullupdate": #being compatible with older versions, which will never exist longer than 1 time pressing F5...
            self.updatePlayerStatisInfo()
            cover_info = self.getCover(moc.info())
            if cover_info["status"]<0:
                return cover_info
            return {"status": 1, "info": self.info, "history": self.played_history, "history_index":self.playing_index, "cover":cover_info["cover"]}
        
        if cmd.lower() == "cover":
            return self.getCover(moc.info())
        
        if cmd.lower() == "history":
            return {"status": 4, "history": self.played_history, "history_index":self.playing_index}#[id,bpm,path]
        
        if cmd.lower().startswith('changebpm&pitch='):
            rg = re.compile('(changebpm&pitch=)'+'([-+]?)'+'(\\d+)',re.IGNORECASE|re.DOTALL)
            m = rg.search(cmd.lower())
            if m:
                print(m.group(0),m.group(1),m.group(2),m.group(3))
                if m.group(2)=='':
                    self.bpmShift = int(m.group(3))
                if m.group(2)=='-':
                    self.bpmShift -= int(m.group(3))
                if m.group(2)=='+':
                    self.bpmShift += int(m.group(3))
                self.info["bpmShift"] = self.bpmShift
                self.updatePlayerStatisInfo()
                
                return {"status": 2, "info": self.info}
            return {"status": -204, "error": "Error in Regular Expression. Does not Match ([-+]?\\d+) Integer."}    
        if cmd.lower().startswith('seek&percentage='):
            rg = re.compile('(seek&percentage=)'+'([+-]?\\d*\\.\\d+)(?![-+0-9\\.])',re.IGNORECASE|re.DOTALL)
            m = rg.search(cmd.lower())
            if m:
                percentage = float(m.group(2))    
                self.seek(percentage)
                self.updatePlayerStatisInfo()
                return {"status": 5, "info": self.info}
            rg = re.compile('(seek&percentage=)'+'(\\d+)',re.IGNORECASE|re.DOTALL)
            m = rg.search(cmd.lower())
            if m:
                percentage = float(m.group(2))    
                self.seek(percentage)
                self.updatePlayerStatisInfo()
                return {"status": 5, "info": self.info}
            return {"status": -205, "error": "Error in Regular Expression. Does not Match ([+-]?\\d*\\.\\d+)(?![-+0-9\\.]) Float."}    
            
        if cmd.lower() == self.shutdownCommand:
            self.softQuit();
        else:
            return {"status": -201, "error": "Error: command " + cmd + " not found"}
    
    def getBestMatch(self,bpm,diff): #remember to add bpm pitch to bpm.
        db = sqlite3.connect("music.db") #changed extention
        c = db.cursor()
        c.execute('SELECT * FROM "music" WHERE "bpm" >= ? AND "bpm" <= ? ORDER BY ABS("bpm" - ?) ASC;', (bpm - diff, bpm + diff, bpm)) #TODO bpm / 2, bpm * 2 
        for song in c: 
                            # (index, bpm, file)  #index starts at 1!
                            # (1, -1, u'/music/SUBFOLDER/(I Want to Wear) Yellow & Blue - TalkAcanthi - Rocking is Magic.mp3')
            song
            if self.debug:
                print("Match> Song is %s" % song[2])
            was_played = False
            for i in self.played_history:
                if song[0] == i["id"]:
                    was_played = True
            if was_played:
                if self.debug:
                    print("Match> Already played, skipping.")
                continue
            audiofile = eyed3.load(song[2]) #path
            bpm = audiofile.tag.bpm
            self.played_history.append({"id":       song[0],
                                        "bpm":      song[1],
                                        "path":     song[2],
                                        "title":    audiofile.tag.title,
                                        "album":    audiofile.tag.album,
                                        "artist":   audiofile.tag.artist
                                        })
            self.playing_index=len(self.played_history)-1 #Reset 
            db.close()
            return song #stop here            
            
        db.close()
        return self.getBestMatch(bpm,diff+5)
        
    def playSong(self,file):
        moc.quickplay([file])
        print("playSong> Waiting for Song to load...")
        songInfo =  moc.current_track_info()
        while(songInfo['state']==0):
            print("playSong> Still waiting for Song to load...")
            songInfo =  moc.current_track_info()
            time.sleep(0.01)
        print(songInfo);
        if not songInfo['state'] == 0:
            self.autoplaynext_enabled = True
            self.autoplaynext_endtime = time.time() + (( int(songInfo['totalsec']) - int(songInfo['currentsec']) ))
        return songInfo
    
    def pauseSong(self):
        songInfo = moc.pause()
        self.autoplaynext_enabled = False
        
    def resumeSong(self):
        songInfo = moc.unpause()
        songInfo =  moc.current_track_info()
        while(songInfo['state']==0):
            print("playSong> Still waiting for Song to load...")
            songInfo =  moc.current_track_info()
            time.sleep(0.01)
        if not songInfo['state'] == 0:
            self.autoplaynext_enabled = True
            self.autoplaynext_endtime = time.time() + ((songInfo['totalsec'] - songInfo['currentsec'])*1000)

        return songInfo
    
    def getPlayerStatus(self,songInfo = moc.info()):
        #print("getPlyrStats> moc.info() returns")
        #print(songInfo)
        if songInfo['state']==0:
            parsedInfo = {
                "id": -1,
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
            
            artwork_string = ""
            parsedInfo = {
                "title": songInfo['songtitle'],
                "album": songInfo['album'], 
                "artist": songInfo['artist'], 
                "currentsec": songInfo['currentsec'],
                "totalsec": songInfo['totalsec'],
                "bpm":bpm,
                "file": songInfo['file'],
                "playingstate": songInfo['state'], #playing state
                "cover": artwork_string
                }   
        return parsedInfo
    
    def getCover(self,songInfo=moc.info()):
        if songInfo['state'] == 0:
            return {"status": -202, "error": "Nothing Playing."}
        artwork = ""
        try:
            file = File(songInfo['file'])
            artwork = file.tags['APIC:'].data
            artwork_string = "data:image/jpeg;charset=utf-8;base64," + base64.b64encode(artwork)
        except KeyError:
            with open("www/no-cover.jpg", "rb") as image_file:  #todo: add to config
                artwork = image_file.read()
                encoded_string ="data:image/jpeg;charset=utf-8;base64," + base64.b64encode(artwork)
                print("loading no-cover.jpg as cover")
            print(encoded_string)
            #self.cover_data = artwork
            #stream = io.BytesIO(artwork)
            #im = Image.open(stream)
            #im = ImageOps.fit(im, (500,100), Image.ANTIALIAS)
            #output = StringIO()
            #im.save(output, "PNG")
            #contents = output.getvalue()
            self.cover_data = artwork
            artwork_string = "data:image/jpeg;charset=utf-8;base64," + encoded_string
            return {"status": -203, "error": "File has no Cover.", "cover":artwork_string }
        print("loading atwork cover as cover")

        #self.cover_small = contents
        self.cover_data = artwork
        return {"status": 3, "cover":artwork_string}

    def updatePlayerStatisInfo(self):
        songInfo = moc.info()
        self.info["song"] = self.getPlayerStatus(songInfo)
        self.info["history_index"] = self.playing_index
        try:
            if (songInfo["file"] != self.last_file): #changed?
                self.getCover(songInfo)
                self.last_file = songInfo["file"]
        except KeyError:
                if self.debug:
                    print("updatePlayerStatisInfo> No File Playing.")
        
    def seek(self,percentage):
        songInfo = moc.info();
        percentage_multiplicator = float(float(songInfo["totalsec"])/100) #float(songInfo["currentsec"])
        print("SEEK> New Jackpot Multiplicator: %f" % percentage_multiplicator)
        time_to_seek_to = round(percentage * percentage_multiplicator)
        time_to_seek_with = int(time_to_seek_to - int(float(songInfo["currentsec"])) )
        print("SEEK> from %s (of %s) time to seek to %f, with %f that's %i (+%i) seconds" % (songInfo["currentsec"], songInfo["totalsec"],percentage, percentage_multiplicator, time_to_seek_to, time_to_seek_with))
        moc.seek(time_to_seek_with)
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
    
    def resize(img,percent):
        ''' Resize image input image and percent | Keep aspect ratio'''
        w,h = img.size
        1/0; #because function should not be called
        return img.resize(((percent*w)/100,(percent*h)/100))

#moc.start_server()
print("INIT> starting bmp server.")  
BPMServer().run()
print("INIT> started both servers.")
#keep_running = True    
  

