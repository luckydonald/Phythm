Phythm
======

The real Phythm Project


Installation
---------------


  - Go home
	* $ `cd ~` (But you can use any directory you have write privileges on)
	* $ `mkdir Phythm`
	* $ `cd Phythm`


	- pip (python package installation)
		* $ `sudo apt-get install -y python-dev`
		* $ `curl -O http://python-distribute.org/distribute_setup.py`
		* $ `sudo python distribute_setup.py`
		* $ `curl -O https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py`
		* $ `sudo python get-pip.py
		* $ `rm *` (Remove that downloaded files, we wont need them anymore.)

	- virtualenv (To have it nice and clean, and don't let other installs interference you.)
		* $ `sudo pip install virtualenv`
		* $ `virtualenv env`
		* And activate it:
		* $ `. env/bin/activate`
		* You may notice the change in your promt, that is only relevant for python.
		
		
	- eyeD3 library (Reads the ID3 tags)
		* $ `pip install eyeD3` 
		* If that fails try instead
		* $ `pip install eyeD3 --allow-external eyeD3 --allow-unverified eyeD3`
		* This enables the download from the external developers homepage (http://eyed3.nicfit.net/)
		
	- mutagen (cover art)
		* $ `pip install mutagen` 

		
  - moc player
  	* $ `sudo apt-get install alsa-utils` (Audio driver)
  	* $ `sudo apt-get install -y moc`
  	* $ `pip install moc`
		You can try out moc as player by launching it with $ `mocp`
		To exit the client press `q`, with `Q` you will shutdown the moc server.
			
1. **Download Phythm source.**
	* $ `git clone https://github.com/Phythm/Phythm.git`
	
	
2. Configure
	* Run `Phythm.py` once to write the default configuration, and edit it.
	* $ `cd Phythm`
	* $ `python Phythm.py`
	* $ `nano config.json`
	
	* Now edit the settings, especially the GPIO Port, and the music directory might need attantion.
	* e.g. `"GPIO": 25,`
	* e.g. `"music_path": "/home/pi/music/"`.
	* Note that the music path has to be absolute, or relative to this directory. `~/music/` does not work!
	
3. **Music!**
	* Get your music on your Pi. I use Cyberduck with sftp (SSH) upload, but you may use other software or scp.
	* Now run `python Phythm.py` again to scan the music folder.
	
	
