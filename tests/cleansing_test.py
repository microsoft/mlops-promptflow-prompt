"""In this class we implement unit tests for cleansing.py in named_entity_recognition flow."""
import unittest
from flows.named_entity_recognition.standard.cleansing import cleansing


class TestCleansing(unittest.TestCase):
    """
    A class that contains unit tests implementation for methods in cleansing.py \
        for named_entity_recognition flow.

    Methods
    -------
    test_normal()
        Tests cleansing method from cleansing.py
    """

    def test_normal(self):
        """The method tests cleansing method that split text using commas and removes trailing \
            whitespaces, dots and tabs."""
        self.assertEqual(cleansing("a, b, c"), ["a", "b", "c"])
        self.assertEqual(
            cleansing("a, b, (425)137-98-25, "), ["a", "b", "(425)137-98-25"]
        )
        self.assertEqual(
            cleansing("a, b, F. Scott Fitzgerald.,  d"),
            ["a", "b", "F. Scott Fitzgerald", "d"],
        )
        self.assertEqual(cleansing("a, b, c,  None., "), ["a", "b", "c", "None"])
        self.assertEqual(cleansing(",,"), [])
        self.assertEqual(cleansing(""), [])
