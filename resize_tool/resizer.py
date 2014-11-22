import os
import threading
from queue import Queue

from PIL import Image
from PIL.ImageDraw import ImageDraw


class Resizer(object):
    def __init__(self):
        self.source_folder = ""
        self.destination_folder = ""

        self.output_width = 640
        self.output_height = 480

        self.copyright_text = None
        self.copyright_alpha = 80

        self.file_name_pattern = None
        self.file_name_pattern_seq_start_num = 0

        self.__current_seq_value = 0
        self.__seq_step = 1
        self.__supported_extensions = ('jpeg', 'jpg',)
        self.__file_names_to_resize = ()
        self.__image_queue = Queue()

        self.lock = threading.Lock()
        self.__threads_num = 3
        self.__processed_images = 0
        self.__resized_images = ()

        self.__horizontal_copyright = None
        self.__vertical_copyright = None

    @staticmethod
    def is_folder_readable(folder):
        return os.access(folder, os.R_OK)

    @staticmethod
    def is_folder_writable(folder):
        return os.access(folder, os.W_OK)

    @staticmethod
    def get_all_files_in_folder(folder):
        all_files = []
        for (dirpath, dirnames, filenames) in os.walk(folder):
            all_files.extend(filenames)
            break
        return all_files

    def __increase_seq_value(self):
        self.__current_seq_value += self.__seq_step

    def __get_last_seq_value(self):
        return self.__current_seq_value

    def set_current_seq_value(self, seq_value):
        if type(seq_value) != int:
            raise ValueError("Sequence start value must be integer")

        self.__current_seq_value = seq_value

    def set_file_name_pattern(self, pattern):
        if type(pattern) != str:
            raise ValueError("Pattern is not string")

        if "$$" not in pattern:
            raise ValueError("Pattern has not $$ mark")

        self.file_name_pattern = pattern

    def set_seq_step(self, step):
        if type(step) != int:
            raise ValueError("Sequence step value must be integer")
        self.__seq_step = step

    def set_source_folder(self, folder):
        if not Resizer.is_folder_readable(folder):
            raise LookupError("Folder is not readable")

        self.source_folder = folder

    def set_destination_folder(self, folder):
        if not Resizer.is_folder_readable(folder):
            raise LookupError("Folder is not readable")

        if not Resizer.is_folder_writable(folder):
            raise LookupError("Folder is not writable")

        self.destination_folder = folder

    def set_copyright_text(self, text):
        if type(text) != str:
            raise ValueError("Copyright text is not string")

        self.copyright_text = text

    def set_copyright_alpha(self, alpha_percent):
        if type(alpha_percent) != int:
            raise ValueError("Alpha is not a integer")

        if alpha_percent not in range(0, 100):
            raise ValueError("Alpha mut be in (0,100) range")

        self.copyright_alpha = alpha_percent

    def set_config_by_dict(self, config_dict):
        if 'source_folder' in config_dict.keys():
            self.set_source_folder(config_dict['source_folder'])

        if 'destination_folder' in config_dict.keys():
            self.set_destination_folder(config_dict['destination_folder'])

        if 'file_name_pattern' in config_dict.keys():
            self.set_file_name_pattern(config_dict['file_name_pattern'])

        if 'file_name_pattern_seq_start_num' in config_dict.keys():
            self.set_current_seq_value(config_dict['file_name_pattern_seq_start_num'])

        if 'output_width' in config_dict.keys():
            self.output_width = config_dict['output_width']

        if 'output_height' in config_dict.keys():
            self.output_height = config_dict['output_height']

        if 'copyright_text' in config_dict.keys() and config_dict['copyright_text']:
            self.set_copyright_text(config_dict['copyright_text'])

        if 'copyright_alpha' in config_dict.keys():
            self.set_copyright_alpha(config_dict['copyright_alpha'])

    def check_config(self):
        assert (type(self.source_folder) == str)
        assert (type(self.destination_folder) == str)

        if self.copyright_text:
            assert (type(self.copyright_text) == str)
            assert (type(self.copyright_alpha) == int)

        assert (type(self.file_name_pattern) == str)
        assert (type(self.file_name_pattern_seq_start_num) == int)

        return True

    def create_filename(self):
        current_value = self.__get_last_seq_value()
        return self.file_name_pattern.replace("$$", str(current_value)).lower()

    def convert_all_source_images_to_jpg(self):
        all_files_in_folder = self.get_all_files_in_folder(self.source_folder)
        all_files_in_folder_abs_path = [os.path.join(self.source_folder, file) for file in all_files_in_folder]

        for infile in all_files_in_folder_abs_path:
            f, e = os.path.splitext(infile)
            outfile = f + ".jpg"
            if infile.lower() != outfile.lower():
                try:
                    Image.open(infile).save(outfile)
                    self.__file_names_to_resize += (outfile, )
                except IOError:
                    try:
                        os.unlink(infile)
                    except Exception:
                        pass
            else:
                self.__file_names_to_resize += (infile, )

    def __put_images_to_queue(self):
        for item in self.__file_names_to_resize:
            self.__image_queue.put(item)

    def get_images_to_process(self):
        self.convert_all_source_images_to_jpg()
        self.__file_names_to_resize = tuple(sorted(self.__file_names_to_resize))

        self.__put_images_to_queue()

        return self.__file_names_to_resize

    def worker(self):
        while True:
            item = self.__image_queue.get()
            self.resize_the_image(item)
            self.__image_queue.task_done()

    def resize_images(self):
        if self.is_copyright():
            self.generate_copyright_images()

        for i in range(self.__threads_num):
            t = threading.Thread(target=self.worker)
            t.daemon = True
            t.start()

        self.__image_queue.join()

    def __increase_processed_images(self):
        self.__processed_images += 1

    def get_count_of_processed_images(self):
        return self.__processed_images

    def is_copyright(self):
        return self.copyright_text and self.copyright_alpha in range(0, 101)

    def resize_the_image(self, infile):
        filename = self.create_filename()
        new_file_path = os.path.join(self.destination_folder, filename)
        im = Image.open(infile)
        align = "horizontal"
        size = (self.output_width, self.output_height)
        if im.size[0] <= im.size[1]:
            size = (self.output_height, self.output_width)
            align = "vertical"
        new_image = im.resize(size, Image.ANTIALIAS)

        self.__increase_seq_value()
        self.__increase_processed_images()
        self.__resized_images += (new_file_path,)

        if self.is_copyright():
            if align == "horizontal":
                copyright_layer = self.__horizontal_copyright
            else:
                copyright_layer = self.__vertical_copyright

            new_image = new_image.convert('RGBA')
            out = Image.alpha_composite(new_image, copyright_layer)
            out.save(new_file_path)
        else:
            new_image.save(new_file_path)

        del im
        del new_image

    def count_opacity_num(self):
        return round(255 * ((100 - self.copyright_alpha) / 100.0))

    def count_copyright_text_position(self, size):
        top = round(size[1] / 2.0)
        half_width = round(size[0] / 2.0)
        font_width = 5
        left = half_width - ((font_width * len(str(self.copyright_text))) / 2.0)
        position = (left, top)
        return position

    def __generate_copyright_image(self, size):
        text_layer = Image.new('RGBA', size, (255, 255, 255, 0))

        draw_object = ImageDraw(text_layer)
        opacity = self.count_opacity_num()
        position = self.count_copyright_text_position(size)
        draw_object.text(position, self.copyright_text, fill=(255, 255, 255, opacity))

        return text_layer

    def generate_copyright_images(self):
        self.__horizontal_copyright = self.__generate_copyright_image((self.output_width, self.output_height))
        self.__vertical_copyright = self.__generate_copyright_image((self.output_height, self.output_width))

    def process_images(self):
        self.check_config()

        self.get_images_to_process()

        self.resize_images()

