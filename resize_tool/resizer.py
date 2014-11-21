import os

from PIL import Image
from PIL.ImageDraw import ImageDraw


class Resizer(object):
    def __init__(self):
        self.source_folder = ""
        self.destination_folder = ""

        self.output_weight = 640
        self.output_height = 480

        self.copyright_text = None
        self.copyright_alpha = 80

        self.file_name_pattern = None
        self.file_name_pattern_seq_start_num = 0

        self.__current_seq_value = 0
        self.__seq_step = 1
        self.__supported_extensions = ('jpeg', 'jpg',)
        self.__filenames_to_resize = ()

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
        # todo move
        self.__increase_seq_value()
        return self.file_name_pattern.replace("$$", str(current_value)).lower()

    def convert_all_source_images_to_jpg(self):
        all_files_in_folder = self.get_all_files_in_folder(self.source_folder)
        all_files_in_folder_abs_path = [os.path.join(self.source_folder, file) for file in all_files_in_folder]

        for infile in all_files_in_folder_abs_path:
            f, e = os.path.splitext(infile)
            outfile = f + ".jpg"
            if infile != outfile:
                try:
                    Image.open(infile).save(outfile)
                    self.__filenames_to_resize += (outfile, )
                except IOError:
                    os.unlink(infile)
            else:
                self.__filenames_to_resize += (outfile, )

    def get_images_to_process(self):
        self.convert_all_source_images_to_jpg()

        return self.__filenames_to_resize

    def process_images(self):
        self.check_config()

        self.get_images_to_process()

        self.resize_images()

        self.add_copyright()

    def resize_images(self):
        for infile in self.__filenames_to_resize:
            filename = self.create_filename()
            new_file_path = os.path.join(self.destination_folder, filename)

            im = Image.open(infile)
            size = (self.output_weight, self.output_height)
            if im.size[0] <= im.size[1]:
                size = (self.output_height, self.output_weight)

            new_image = im.resize(size, Image.ANTIALIAS)
            new_image.save(new_file_path)

            del im
            del new_image

    def add_copyright(self):
        if not self.copyright_text or self.copyright_alpha not in range(0, 101):
            return

        all_files_in_folder = self.get_all_files_in_folder(self.destination_folder)
        files_to_copyright = [os.path.join(self.destination_folder, file) for file in all_files_in_folder]

        for infile in files_to_copyright:
            base = Image.open(infile).convert('RGBA')

            txt = Image.new('RGBA', base.size, (255, 255, 255, 0))

            d = ImageDraw(txt)

            opacity = round(255 * ((100 - self.copyright_alpha) / 100.0))
            top = round(base.size[1] / 2.0)
            half = round(base.size[0] / 2.0)

            magic_mum = 5
            left = half - ((magic_mum * len(str(self.copyright_text))) / 2.0)
            position = (left, top)

            d.text(position, self.copyright_text, fill=(255, 255, 255, opacity))
            out = Image.alpha_composite(base, txt)
            out.save(infile)

