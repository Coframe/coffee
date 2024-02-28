import unittest
import os
import sys
from unittest import mock


from main import extract_tag


class TestExtractTag(unittest.TestCase):

    def test_extract_simple_tag(self):
        content = "<Coffee>Content</Coffee>"
        expected = {
          "match": mock.ANY,  # This will be a regex match object
          "tag": "Coffee",
          "props": {},
          "children": "Content",
          "attributes": ""
        }
        self.assertEqual(extract_tag(content, "Coffee"), expected)

    def test_extract_tag_with_attributes(self):
        content = '<Component coffee="true">Hello</Component>'
        expected = {
          "match": mock.ANY,
          "tag": "Component",
          "props": {"coffee": "true"},
          "children": "Hello",
          "attributes": 'coffee="true"'
        }
        self.assertEqual(extract_tag(content, "Component", 'coffee="true"'), expected)

    def test_extract_nonexistent_tag(self):
        content = "<Tea>Content</Tea>"
        self.assertIsNone(extract_tag(content, "Coffee"))
