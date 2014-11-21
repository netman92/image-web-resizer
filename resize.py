import sys

import yaml

from resize_tool.resizer import Resizer


try:
    stream = open("config.yml", 'r')
except FileNotFoundError:
    print("File 'config.yml' not found")
    sys.exit(-1)

config_dict = yaml.load(stream)

tool = Resizer()
tool.set_config_by_dict(config_dict)
tool.process_images()