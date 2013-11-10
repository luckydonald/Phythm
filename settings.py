import os, json

conf = {}

default = {
        "port":                          8080,
        "music_path":                   ".",
        "audio_types":             ['audio/mpeg'],
        "max_diff":                     20,
        "tick_gpio":                    0,
        "average":						20,  						#TODO: Needs better name
        "timeout":						5,   # value in seconds		#TODO: Needs better name
        "GPIO":                         4
        }

config_file = "config.json"

needs_update = False

if os.path.exists(config_file):
    print("reading configuration from " + config_file)
    cfgs = open(config_file, "r").read()
    if cfgs == "":
        conf = default
        needs_update = True
    else:
        cfg = json.loads(cfgs)
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
    file.flush()
    file.close()
