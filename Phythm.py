#
#
# TODO: line 34 - Move MIME Types to setting .json
#
#

import mimetypes
import settings
import sqlite3
import eyed3
import glob
import os

############################
 ##########################
  ##                    ##
  ##      Functions     ##
  ##                    ##
 ##########################
############################

def processFile(currentDir):
    ''' Process video files within this directory. '''
    # Get the absolute path of the currentDir parameter
    currentDir = os.path.abspath(currentDir)
    # Get a list of files in currentDir
    filesInCurDir = os.listdir(currentDir)
    
    # Traverse through all files
    for file in filesInCurDir:
        curFile = os.path.join(currentDir, file)
        
        # Check if it's a normal file or directory
        if os.path.isfile(curFile):
            curFileExtension = mimetypes.guess_type(curFile)[0]
            #print('Guessing file type for "%s": %s' %(curFile, curFileExtension))
            # Get the file extension
            
            # Check if the file has an extension of typical music files
            if curFileExtension in ['audio/mpeg']:
                # We have got a audio file! Increment the counter
                processFile.counter += 1
                
                # Print it's name
                audiofile = eyed3.load(curFile)
                bpm = audiofile.tag.bpm
                if bpm == None:
                    bpm = 0
                print('=> Found fitting \'%s:\' file with %3d BPM: %s '% (curFileExtension,bpm,unicode(curFile)))
                c.execute("INSERT INTO music VALUES (NULL,?,?)" , (bpm, unicode(curFile)))
        else:
            # We got a directory, enter into it for further processing
            #print('# Found dir: %s' % curFile)
            processFile(curFile)
                
            

                
                
############################
 ##########################
  ##                    ##
  ##         Main       ##
  ##                    ##
 ##########################
############################
processFile.counter = -1

if __name__ == '__main__':
    # Get the current working directory
    currentDir = os.getcwd()
    currentDir = songdir = settings.conf["music_path"]
 #"/music"
    print('=== Creating Database === ')

    print('Starting processing in %s' % currentDir)
    
    # Set the number of processed files equal to zero
    processFile.counter = 0
    processFile.list = []
    
    sqlconn = sqlite3.connect('music.db')
    
    #lets get a cursor!
    c = sqlconn.cursor()
    
    #drop old Database    
    c.execute('''DROP TABLE IF EXISTS music''')

    #create table
    #            
    #        ID     |  BPM  |  PATH            
    #        0      |  199  |  /music/song.mp3 
    #
    #print(' |-> Creating Table')

    
    c.execute('''CREATE TABLE music (id  INTEGER PRIMARY KEY, bpm int, path text)''')
    
    # Start Processing
    processFile(currentDir)
    
    sqlconn.commit()
    sqlconn.close()


