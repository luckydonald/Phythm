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
		
	- eyeD3 library (Reads the ID3 tags)
		* $ `sudo pip install eyeD3` 
		* If that fails try instead
		* $ `sudo pip install eyeD3 --allow-external eyeD3 --allow-unverified eyeD3`
		* This enables the download from the external developers homepage (http://eyed3.nicfit.net/)
		
	- mutagen (cover art)
		* $ `sudo pip install mutagen` 

		
  - moc player
  	* $ `sudo apt-get install alsa-utils` (Audio driver)
  	* $ `sudo apt-get install -y moc`
  	* $ `sudo pip install moc`
		You can try out moc as player by launching it with __$__ `mocp`
		To exit the client press `q`, with `Q` you will shutdown the moc server.
			
1. **Download Phythm source.**
	* $ `cd ..`
	* $ `git clone https://github.com/Phythm/Phythm.git`
	
	
2. **Configure**
	* Run `Phythm.py` once to write the default configuration, and edit it.
	* $ `cd Phythm`
	* $ `python Phythm.py`
	* $ `nano config.json`
	
	* Now edit the settings, especially the GPIO Port, and the music directory might need attantion.
	* e.g. `"GPIO": 25,`
	* e.g. `"music_path": "/home/pi/music/"`.
	* Note that the music path has to be absolute, or relative to this directory. `~/music/` does not work!
	
3. **Scan for Music**
	* Get your music on your Pi. I use Cyberduck with sftp (SSH) upload, but you may use other software or scp.
	* Now scan the music folder.
	* $ `python Phythm.py`
	* If you changed the music, you have to run it again to appear in Phythm.

4. **Run It**
	* Now, if it found music you can start up the server.
	* Fire up the Moc server, using the root user, so our script can access.
	* $ `sudo mocp -S`
	* You need root to set portnumbers smaller then 100 and to access the GPIOs.
	* $ `sudo python server.py`
	* 
5. **Troubleshooting**
	* If your console get fooded with errors, ending with something like this:
	``` shell
	Exception: attempting to use libmagic on multiple threads will end in SEGV.  Prefer to use the module functions from_file or from_buffer, or carefully manage direct use of the Magic class
	----------------------------------------
	```
	then eyeD3 is still broken, you have to compile it from source. This is much to do, but not really complex.
	* $ `sudo pip uninstall -y eyeD3`
	* $ `mkdir eyeD3_temp`
	* $ `cd eyeD3_temp`
	* $ `sudo apt-get install -y mercurial`
	* $ `hg clone https://bitbucket.org/nicfit/eyed3`
	* $ `cd eyed3`
	* $ `sudo python setup.py install`
	* $ `cd ../..`
	* $ `sudo rm eyeD3_temp/ -R -f` We don't need it, it is installed.
	* Now retry `sudo python server.py`.
	
