import unittest
from src.utils import vaheguru_check, vaheguru_key_words


class UtilsTest(unittest.TestCase):
    def test_vaheguru_check_good(self):
        for key_word in vaheguru_key_words:
            test_string = f"You're a very cool person, may {key_word} bless you..."
            self.assertTrue(vaheguru_check(test_string))

    def test_vaheguru_check_substring(self):
        for key_word in vaheguru_key_words:
            test_string = f"This string should return false some{key_word}word"
            self.assertFalse(vaheguru_check(test_string))

    def test_vaheguru_check_no_key_word(self):
            test_string = "This message contains no key word that can be picked up by the handler"
            self.assertFalse(vaheguru_check(test_string))


if __name__ == '__main__':
    unittest.main()
