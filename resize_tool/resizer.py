import os


class Resizer:
    def __init__(self):
        self.source_folder = None
        self.destination_folder = None

        self.output_weight = 640
        self.output_height = 480

        self.copyright_text = None
        self.copyright_alpha = 80

        self.file_name_pattern = None
        self.file_name_pattern_seq_start_num = 0

        self.__current_seq_value = 0
        self.__seq_step = 1
        self.__supported_extensions = ('png', 'jpeg', 'jpg',)

    @staticmethod
    def is_folder_readable(folder):
        return os.access(folder, os.R_OK)

    @staticmethod
    def is_folder_writable(folder):
        return os.access(folder, os.W_OK)

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