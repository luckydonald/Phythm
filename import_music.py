import sqlite3

db = sqlite3.connect("music.sqlite")

c = db.cursor()

c.execute("DROP TABLE IF EXISTS music;")  # delete table if it exists
c.execute("CREATE TABLE music (id INT , bpm INT ,path TEXT);") # create table

music = []

print("Scanning for music files!")

#scan music files and insert a dict with keys 'bpm' and 'path' into 'music'

#some data for testing
music = [{"bpm": 120    , "path": "testpath1"},
         {"bpm": 80     , "path": "testpath2"},
         {"bpm": 100    , "path": "testpath3"},
         {"bpm": 65     , "path": "testpath4"},
         {"bpm": 74     , "path": "testpath5"},
         {"bpm": 137    , "path": "testpath6"}]


print("Found " + str(len(music)) + " files!")

i = 0

for file in music:
    c.execute('INSERT INTO "music" VALUES (?, ?, ?);', (i, file['bpm'], file["path"]))
    i += 1

db.commit()
c.close()

print("Done!")