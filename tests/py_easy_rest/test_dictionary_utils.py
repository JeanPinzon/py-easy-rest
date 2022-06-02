from unittest import TestCase

from py_easy_rest.dictionary_utils import merge


class TestDictionaryUtils(TestCase):

    def test_should_merge_correctly(self):
        dict_a = {'first': {'all_rows': {'pass': 'dog', 'number': '1'}}}
        dict_b = {'first': {'all_rows': {'fail': 'cat', 'number': '5'}}}

        expected_dict = {'first': {'all_rows': {'pass': 'dog', 'fail': 'cat', 'number': '5'}}}

        result = merge(dict_b, dict_a)

        assert result == expected_dict
