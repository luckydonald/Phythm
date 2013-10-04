import sqlite3, settings, eyed3, os

db = sqlite3.connect("music.sqlite")

c = db.cursor()

c.execute("DROP TABLE IF EXISTS music;")  # delete table if it exists
c.execute("CREATE TABLE music (id INT , bpm INT ,path TEXT);") # create table

music = []

scan_dir = settings.music_path
ext = settings.music_extensions

print("Scanning for music files!")

#scan music files and insert a dict with keys 'bpm' and 'path' into 'music'

def getBPM(file):
    audiofile = eyed3.load(file)
    print("BPM of " + file + " is " + str(audiofile.tag.bpm))
    return audiofile.tag.bpm

def scan(top):
    print("Scanning: " + top)
    list = []
    for f in os.listdir(top):
        if os.path.isdir(f):
            for file in scan(f):
                list.append(file)
        else:
            parts = f.split(".")
            if parts[len(parts) - 1] in ext:
                f = os.path.join(scan_dir, f)
                list.append({"path": f, "bpm": getBPM(f)})
    return list

music = scan(scan_dir)  # scan music dictionary

print("Found " + str(len(music)) + " files!")

i = 0

for file in music:
    c.execute('INSERT INTO "music" VALUES (?, ?, ?);', (i, file['bpm'], unicode(file["path"])))
    i += 1

db.commit()
c.close()

print("Done!")