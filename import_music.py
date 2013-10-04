import sqlite3, settings

db = sqlite3.connect("music.sqlite")

c = db.cursor()

c.execute("DROP TABLE IF EXISTS music;")  # delete table if it exists
c.execute("CREATE TABLE music (id INT , bpm INT ,path TEXT);") # create table

music = []

scan_dir = settings.music_path

print("Scanning for music files!")

#scan music files and insert a dict with keys 'bpm' and 'path' into 'music'

def getBPM(file):
    print("getting bpm of " + file)

def scan(top):
    print("Scanning: " + top)
    list = []
    for f in os.listdir(top):
        if os.path.isdir(f):
            for file in scan(f):
                list.append(file)
        else:
            list.append({"path": os.path.abspath(f), "bpm": getBPM(os.path.abspath(f))})
    return list

#music = scan(scan_dir)  # scan music dictionary

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