#
#
# TODO:
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
    filesInCurDir = os.listdir(unicode(currentDir))
    files_without_bpm = []
    # Traverse through all files
    for file in filesInCurDir:
        curFile = os.path.join(currentDir, file)
        #curFile = curFile.encode('utf-16')
        
        # Check if it's a normal file or directory
        if os.path.isfile(curFile):
            curFileExtension = mimetypes.guess_type(curFile)[0]
            #print('Guessing file type for "%s": %s' %(curFile, curFileExtension))
            # Get the file extension
            
            # Check if the file has an extension of typical music files
            if curFileExtension in settings.conf["audio_types"]:
                # We have got a audio file! Increment the counter
                processFile.counter += 1
                
                # Print it's name
                # print("Loading file: " + curFile)
                audiofile = eyed3.core.load(curFile)
                if audiofile == None:
                    files_without_meta.append(curFile)
                    print('=> Corrupted Metadata: %s' % curFile)
                else:
                    bpm = audiofile.tag.bpm
                    if bpm == None:
                        bpm = 0;
                        files_without_bpm.append(curFile)
                        print('=> NOT fitting \'%s:\' file with %3d BPM: %s '% (curFileExtension,bpm,curFile))

                    else:
                        print('=> Found fitting \'%s:\' file with %3d BPM: %s '% (curFileExtension,bpm,curFile))
                        c.execute("INSERT INTO music VALUES (NULL,?,?)" , (bpm, curFile))
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
    #currentDir = os.getcwd()
    currentDir = settings.conf["music_path"]   #for example "/music"
    global files_without_bpm
    files_without_bpm = []
    files_without_meta = []
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

    
    c.execute('''CREATE TABLE music (id  INTEGER PRIMARY KEY, bpm int, path text)''') #, int playcount
    
    # Start Processing
    processFile(currentDir)
    print(files_without_bpm)

    for file in files_without_bpm:

        print("Missing BPM Tag in file %s" % file)

    sqlconn.commit()
    sqlconn.close()

    print("=== Done === ")
