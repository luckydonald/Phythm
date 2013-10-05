import os, json

conf = {}

default = {
		"music_path":				  ".",
		"music_extensions":			["mp3", "flac"],
		"max_diff":					20
		}

config_file = "config.json"

needs_update = False

if os.path.exists(config_file):
	print("reading configuration from " + config_file)
	cfg = json.loads(open(config_file, "r").read())
	for key in default.keys():
		if key in cfg:
			conf[key] = cfg[key]
		else:
			conf[key] = default[key]
			needs_update = True
else:
	conf = default
	needs_update = True

if needs_update:
	print("writing configuration to " + config_file)
	file = open(config_file, "w")
	file.write(json.dumps(conf, sort_keys=True, indent=4, separators=(',', ': ')))
