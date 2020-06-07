import unittest
from wub_remover.main import song_decoder


class RequireTestCase(unittest.TestCase):

    def test_tc_001(self):
        self.assertEqual(song_decoder("AWUBBWUBC"), "A B C")

    def test_tc_002(self):
        self.assertEqual(song_decoder("AWUBWUBWUBBWUBWUBWUBC"), "A B C")

    def test_tc_003(self):
        self.assertEqual(song_decoder("WUBAWUBBWUBCWUB"), "A B C")

    def test_tc_004(self):
        self.assertEqual(song_decoder("WUBWUBWUBAWUBBWUBCWUBWUBWUB"), "A B C")


if __name__ == '__main__':
    unittest.main()
