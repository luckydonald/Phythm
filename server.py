import sqlite3

db = sqlite3.connect("music.sqlite")

c = db.cursor()

diff = 20
played = []


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
	
#c.execute("CREATE TABLE music (id INT AUTO_INCREMET, bpm INT ,path TEXT);")
#c.execute('INSERT INTO "music" VALUES ("0", "120", "test");')


for i in range(0, 20):
	print(getBestMatch(100))


#db.commit()
c.close()