import sqlite3
import eyed3
import glob
import os

############################
 ##########################
  ##             ##
  ##      Functions    ##
  ##            ##
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
            # Get the file extension
            curFileExtension = curFile[-3:]
            
            # Check if the file has an extension of typical video files
            if curFileExtension in ['mp3', 'flac']:
                # We have got a audio file! Increment the counter
                processFile.counter += 1
                
                # Print it's name
                print('+ Found file: %s' % curFile)
                processFile.list.append(curFile)
        else:
            # We got a directory, enter into it for further processing
            print('# Found dir: %s' % curFile)
            processFile(curFile)
                
            

    
                
                
############################
 ##########################
  ##             ##
  ##         Main    ##
  ##            ##
 ##########################
############################
processFile.counter = -1

if __name__ == '__main__':
    # Get the current working directory
    currentDir = os.getcwd()
    currentDir = songdir = "/music"
    
    print('Starting processing in %s' % currentDir)
    
    # Set the number of processed files equal to zero
    processFile.counter = 0
    processFile.list = []
    
    # Start Processing
    processFile(currentDir)
    
    # We are done. Continue now. Write Report.
    print(' -- %s Song File(s) found in directory %s/ --' \
      % (processFile.counter, currentDir))
    print(' Press ENTER to continue!')
    
    # Wait until the user presses enter/return
    raw_input()
    
    
    print('=== Creating Database === ')
    
    
    sqlconn = sqlite3.connect('songs.db')
    
    #lets get a cursor!
    c = sqlconn.cursor()
    
    print(' |-> Droping old Database')
    
    c.execute('''DROP TABLE bpm''')
    print(' |-> Creating Database')

    #create table
    #            
    #        ID   |  BPM  |  PATH            | COUNT
    #               0    |  199  |  /music/song.mp3 | 12
    #
    print(' |-> Creating Table')

    
    c.execute('''CREATE TABLE bpm (id  INTEGER PRIMARY KEY, bpm int, path text,count int)''')
    
    for file in processFile.list:
        print(' |')
        print(' |--> Processing file %s' % file)
        print(' ||-> Getting Data')
        audiofile = eyed3.load(file)
        bpm = audiofile.tag.bpm
        print(' ||-> BPM: %s' % bpm)
        if bpm == None:
            bpm = -1
            print(' ||#> changing BPM to : %s' % bpm)
        print(' ||-> Inserting into Database')
        print(' ||-> (INSERT INTO bpm VALUES (NULL,%s,"%s",0)' % (bpm, file))
        c.execute("INSERT INTO bpm VALUES (NULL,%s,\"%s\",0)" % (bpm, file))
        print(' |\-> Done.')
    sqlconn.commit()
    print(' |-> Commited Database')
    sqlconn.close()
    print(' \-> Closed Database')
