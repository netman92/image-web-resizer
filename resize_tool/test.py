import unittest
import os

from PIL import Image

from resize_tool.resizer import Resizer


class TestBaseConfig(unittest.TestCase):
    def test_new_filename_default_step(self):
        resizer = Resizer()

        resizer.set_current_seq_value(50)
        resizer.set_file_name_pattern("OBR_adasdas_$$.jpg")

        self.assertEqual(resizer.create_filename(), "obr_adasdas_50.jpg")

    def test_new_filename_not_default_step(self):
        resizer = Resizer()

        resizer.set_current_seq_value(550)
        resizer.set_file_name_pattern("OBR_adasdas_$$.jpg")
        resizer.set_seq_step(15)

        self.assertEqual(resizer.create_filename(), "obr_adasdas_550.jpg")

    def test_filename_pattern(self):
        resizer = Resizer()

        self.assertRaises(ValueError, resizer.set_file_name_pattern, "test")
        self.assertRaises(ValueError, resizer.set_file_name_pattern, 123)
        self.assertRaises(ValueError, resizer.set_file_name_pattern, None)

    def test_set_current_seq_value(self):
        resizer = Resizer()

        self.assertRaises(ValueError, resizer.set_current_seq_value, "test")

    def test_set_current_seq_step(self):
        resizer = Resizer()

        self.assertRaises(ValueError, resizer.set_seq_step, "test")

    def test_set_copyright_text(self):
        resizer = Resizer()

        self.assertRaises(ValueError, resizer.set_copyright_text, False)

    def test_set_copyright_alpha(self):
        resizer = Resizer()
        self.assertRaises(ValueError, resizer.set_copyright_alpha, False)
        self.assertRaises(ValueError, resizer.set_copyright_alpha, 111)

        resizer.set_copyright_alpha(55)


    def test_folder(self):
        resizer = Resizer()
        resizer.set_source_folder('/tmp/')

        self.assertEqual(resizer.source_folder, '/tmp/')

        self.assertRaises(LookupError, resizer.set_destination_folder, '/var/log/')
        self.assertRaises(LookupError, resizer.set_destination_folder, '/not/existing/folder')

        self.assertRaises(LookupError, resizer.set_source_folder, '/not/existing/folder')

    def test_checker_wrong(self):
        resizer = Resizer()
        self.assertRaises(AssertionError, resizer.check_config)

    def test_checker_good(self):
        resizer = Resizer()
        resizer.set_source_folder('/tmp/')
        resizer.set_destination_folder('/tmp/')
        resizer.set_current_seq_value(550)
        resizer.set_file_name_pattern("OBR_adasdas_$$.jpg")

        self.assertTrue(resizer.check_config)


class TestImagesResizer(unittest.TestCase):
    def rm_whole_folder(self, folder):
        try:
            for file in [os.path.join(folder, f) for f in os.listdir(folder)]:
                os.unlink(file)
            os.removedirs(folder)
        except FileNotFoundError:
            pass

    def setUp(self):
        folder = os.path.join(os.path.realpath('/tmp'), 'test')
        self.rm_whole_folder(folder)

        os.mkdir(folder)

        self.folder = folder

        resizer = Resizer()
        resizer.set_source_folder(folder)
        resizer.set_destination_folder(folder)
        resizer.set_current_seq_value(550)
        resizer.set_file_name_pattern("picture-$$.jpg")
        resizer.set_copyright_text("Test copyright")
        resizer.copyright_alpha = 35

        self.resizer = resizer

    def tearDown(self):
        folder = os.path.join(os.path.realpath('/tmp'), 'test')
        self.rm_whole_folder(folder)

    def test_pictures_in_folder(self):
        with open(os.path.join(self.folder, 'img2.JpEG'), "w+"): pass
        with open(os.path.join(self.folder, 'img.GIF'), "w+"): pass
        with open(os.path.join(self.folder, 'img.PNG'), "w+"): pass
        with open(os.path.join(self.folder, 'img.txt'), "w+"): pass

        Image.new("RGB", (512, 512), "white").save(os.path.join(self.folder, 'real_super_image.JPG'))
        Image.new("RGB", (512, 512), "red").save(os.path.join(self.folder, 'real_super_image2.png'))

        actual = set(self.resizer.get_images_to_process())
        expected = {"/tmp/test/real_super_image2.jpg", "/tmp/test/real_super_image.jpg"}
        self.assertEqual(actual, expected)

    def test_resize_pictures(self):
        Image.new("RGB", (1080, 1960), "red").save(os.path.join(self.folder, 'vertical.jpg'))

        self.resizer.set_current_seq_value(550)
        self.resizer.process_images()

        im = Image.open(os.path.join(self.folder, 'picture-550.jpg'))
        self.assertEqual(im.format, "JPEG")
        self.assertEqual(im.size, (480, 640))

    def test_resize_pictures_no_copyright(self):
        self.resizer.set_copyright_text("")

        Image.new("RGB", (1080, 1960), "red").save(os.path.join(self.folder, 'vertical.jpg'))

        self.resizer.set_current_seq_value(550)
        self.resizer.process_images()

        im = Image.open(os.path.join(self.folder, 'picture-550.jpg'))
        self.assertEqual(im.format, "JPEG")
        self.assertEqual(im.size, (480, 640))
        self.assertEqual(self.resizer.get_count_of_processed_images(), 1)

    def test_config_dict(self):
        self.resizer.set_copyright_text("")
        config_dict = {
            "output_height": 480,
            'copyright_alpha': 80,
            'output_weight': 640,
            'file_name_pattern_seq_start_num': 0,
            'source_folder': self.folder,
            'file_name_pattern': 'picture-$$.jpg',
            'copyright_text': None,
            'destination_folder': self.folder,
        }

        Image.new("RGB", (1080, 1960), "red").save(os.path.join(self.folder, 'vertical.jpg'))

        self.resizer.set_config_by_dict(config_dict)
        self.resizer.process_images()