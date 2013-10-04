import sqlite3, settings, socket, SimpleHTTPServer, SocketServer, threading, time, json, re

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
	
	port = 81
	
	bpmServer = None
	
	def run(self):
		Handler = ModHTTPRequestHandler
		
		Handler.bpmServer = self.bpmServer
	
		httpd = SocketServer.TCPServer(("", self.port), Handler)
	
		print "serving at port", self.port
		httpd.serve_forever()
		
class BPMServer():
	
	db = sqlite3.connect("music.sqlite")

	c = db.cursor()
	diff = settings.max_diff
	
	server = HTTPserver()
	
	played = []
	
	info = {
		"bpm": 0,
		"song": {
				"name": "Songname", 
				"artist": "Songartist", 
				"length": 325
				},
		"pos": 125
		}
	
	def run(self):
		
		print("Starting HTTP Server!")
		
		self.server.daemon = True
		self.server.bpmServer = self
		self.server.start()
		
		
		time.sleep(10)
		
		print("Stop!")
		self.c.close()
		
	def handleCMD(self, cmd):
		print("Handling:" + cmd)
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
