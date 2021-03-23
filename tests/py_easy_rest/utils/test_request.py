from unittest import TestCase

from py_easy_rest.utils.request import get_query_string_arg


class TestRequestUtils(TestCase):

    def test_should_get_arg_return_correct_arg(self):
        query_string = {
            "name": "Jean Pinzon",
        }

        result = get_query_string_arg(query_string, "name")

        assert result == "Jean Pinzon"

    def test_should_get_arg_return_correct_arg_when_it_is_an_array_with_only_one_item(self):
        query_string = {
            "name": ["Jean"],
        }

        result = get_query_string_arg(query_string, "name")

        assert result == "Jean"

    def test_should_get_arg_return_correct_arg_when_it_is_an_array(self):
        query_string = {
            "name": ["Jean", "Alycio"],
        }

        result = get_query_string_arg(query_string, "name")

        assert result == ["Jean", "Alycio"]

    def test_should_get_arg_return_None_when_it_does_not_exists(self):
        query_string = {
            "name": ["Jean", "Alycio"],
        }

        result = get_query_string_arg(query_string, "age")

        assert result is None
