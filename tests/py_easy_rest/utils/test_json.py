from unittest import TestCase

from bson.objectid import ObjectId

from py_easy_rest.utils.json import JSONEncoder


class TestJsonUtils(TestCase):

    json_dumps = JSONEncoder().encode

    def test_should_parse_object_id_to_string(self):
        result = self.json_dumps({"id": ObjectId("551137c2f9e1fac808a5f572")})

        assert result == '{"id": "551137c2f9e1fac808a5f572"}'
