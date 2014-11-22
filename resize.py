import sys
import time

import yaml

from resize_tool.resizer import Resizer


start = time.perf_counter()

try:
    stream = open("config.yml", 'r')
except FileNotFoundError:
    print("File 'config.yml' not found")
    sys.exit(-1)

config_dict = yaml.load(stream)

tool = Resizer()
tool.set_config_by_dict(config_dict)
tool.process_images()

end = time.perf_counter()
print("Processed %d images." % (tool.get_count_of_processed_images(), ))
print('Elapsed time: ', end - start)