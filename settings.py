
# configuration file for Phythm
import platform
print('Your Platform is %s.' % platform.system())
if platform.system() == "Windows":
	music_path          = "I:/r"                # path to the music folder for scanning
else:
	music_path          = "/music"                # path to the music folder for scanning

music_extensions    = ["mp3", "flac"]       # valid extensions for music files

max_diff            = 20                    # maximum difference between searched and found bpm values