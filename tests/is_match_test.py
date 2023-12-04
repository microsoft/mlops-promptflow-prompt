"""In this class we implement unit tests for match.py in named_entity_recognition evaluation flow."""
import unittest
from flows.named_entity_recognition.evaluation.match import is_match


class TestIsMatch(unittest.TestCase):
    """
    A class that contains unit tests implementation for methods in match.py \
        for named_entity_recognition evaluation flow.

    Methods
    -------
    test_normal()
        Tests is_match method from match.py
    """

    def test_normal(self):
        """The method tests is_match method that takes two arrays as parameters,  \
            and it allows us to do matching in ignoring case, order or do partial matching."""
        self.assertEqual(is_match(["a", "b"], ["B", "a"], True, True, False), True)
        self.assertEqual(is_match(["a", "b"], ["B", "a"], True, False, False), False)
        self.assertEqual(is_match(["a", "b"], ["B", "a"], False, True, False), False)
        self.assertEqual(is_match(["a", "b"], ["B", "a"], False, False, True), False)
        self.assertEqual(is_match(["a", "b"], ["a", "b"], False, False, False), True)
        self.assertEqual(is_match(["a", "b"], ["a", "b", "c"], True, False, True), True)
