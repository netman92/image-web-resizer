import unittest

from resize_tool.resizer import Resizer


class TestDefault(unittest.TestCase):
    def test_new_filename_default_step(self):
        resizer = Resizer()

        resizer.set_current_seq_value(50)
        resizer.set_file_name_pattern("OBR_adasdas_$$.jpg")

        self.assertEqual(resizer.create_filename(), "obr_adasdas_50.jpg")
        self.assertEqual(resizer.create_filename(), "obr_adasdas_51.jpg")
        self.assertEqual(resizer.create_filename(), "obr_adasdas_52.jpg")

    def test_new_filename_not_default_step(self):
        resizer = Resizer()

        resizer.set_current_seq_value(550)
        resizer.set_file_name_pattern("OBR_adasdas_$$.jpg")
        resizer.set_seq_step(15)

        self.assertEqual(resizer.create_filename(), "obr_adasdas_550.jpg")
        self.assertEqual(resizer.create_filename(), "obr_adasdas_565.jpg")
        self.assertEqual(resizer.create_filename(), "obr_adasdas_580.jpg")

    def test_filename_pattern(self):
        resizer = Resizer()

        self.assertRaises(ValueError, resizer.set_file_name_pattern, "test")
        self.assertRaises(ValueError, resizer.set_file_name_pattern, 123)
        self.assertRaises(ValueError, resizer.set_file_name_pattern, None)

    def test_folder(self):
        resizer = Resizer()
        resizer.set_source_folder('/tmp/')

        self.assertEqual(resizer.source_folder, '/tmp/')

        self.assertRaises(LookupError, resizer.set_destination_folder, '/var/log/')
        self.assertRaises(LookupError, resizer.set_destination_folder, '/not/existing/folder')

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