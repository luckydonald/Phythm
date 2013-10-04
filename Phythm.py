import sqlite3
import glob
import os

############################
 ##########################
  ## 			##
  ## 	 Functions	##
  ##			##
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
				print('Found file: %s' % curFile)
		else:
			# We got a directory, enter into it for further processing
			print('Found dir: %s' % curFile)
			processFile(curFile)
				
			

	
				
				
############################
 ##########################
  ## 			##
  ## 	    Main	##
  ##			##
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
	
	# Start Processing
	processFile(currentDir)
	
	# We are done. Continue now. Write Report.
	print(' -- %s Song File(s) found in directory %s --' \
	  % (processFile.counter, currentDir))
	print(' Press ENTER to exit!')
	
	# Wait until the user presses enter/return
	raw_input()
	
	
	print('Creating Database')
	
	
	sqlconn = sqlite3.connect('songs.db')
	
	#lets get a cursor!
	c = sqlconn.cursor()
	print('Creating Database')

	
	#create table
	#			
	#		ID   |  BPM  |  PATH
	#               0    |  199  |  /music/song.mp3
	#
	print('Creating Table')

	
	c.execute('''CREATE TABLE bpm (id int, bpm int, path text)''')
	

	
