import sqlite3
sqlconn = sqlite3.connect('songs.db')

#lets get a cursor!
c = sqlconn.cursor()



print 

#create table
#			
#		ID   |  BPM  |  PATH
#               0    |  199  |  /music/
#


c.execute('''CRATE TABLE bpm (id int, bpm int, path text)''')

