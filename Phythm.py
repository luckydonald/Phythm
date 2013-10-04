import sqlite3
import glob
import os

songdir="/music"

sqlconn = sqlite3.connect('songs.db')

#lets get a cursor!
c = sqlconn.cursor()




print 

#create table
#			
#		ID   |  BPM  |  PATH
#               0    |  199  |  /music/song.mp3
#


c.execute('''CREATE TABLE bpm (id int, bpm int, path text)''')

os.chdir(songdir)
for files in glob.glob("*.mp3"):
    print files
