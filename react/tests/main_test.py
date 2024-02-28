import json
import unittest
from unittest import mock
from unittest.mock import mock_open, patch


from react.main import DEFAULT_CONFIG, extract_tag, set_import, parse_config


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


class TestSetImport(unittest.TestCase):
    def test_add_import(self):
        content = "import React from 'react'\n"
        import_statement = "import MyComponent from './MyComponent'\n"
        expected = content + import_statement
        self.assertEqual(set_import(content, import_statement, True), (expected, True))

    def test_remove_import(self):
        import_statement = "import MyComponent from './MyComponent'\n"
        content = "import React from 'react'\n" + import_statement
        expected = "import React from 'react'\n"
        self.assertEqual(set_import(content, import_statement, False), (expected, True))

    def test_import_already_exists(self):
        import_statement = "import React from 'react'\n"
        content = import_statement
        self.assertEqual(set_import(content, import_statement, True), (content, False))

    def test_import_does_not_exist_for_removal(self):
        import_statement = "import MyComponent from './MyComponent'\n"
        content = "import React from 'react'\n"
        self.assertEqual(set_import(content, import_statement, False), (content, False))


class TestParseConfig(unittest.TestCase):
    def test_parse_config_with_valid_file(self):
        mock_file_content = json.dumps({
          "mount": "./test_components",
          "patterns": ["**/*.test.js"],
          "metadata": {"date": "2024-01-01"}
        })
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            result = parse_config("dummy/path/config.json")
        expected = {
            "mount": "./test_components",
            "patterns": ["**/*.test.js"],
            "example": None,
            "metadata": {"date": "2024-01-01"}
        }
        self.assertEqual(result, expected)

    def test_parse_config_with_invalid_file(self):
        with patch("builtins.open", mock_open(read_data="{invalid json")):
            with self.assertRaises(json.JSONDecodeError):
                parse_config("dummy/path/config.json")

    def test_parse_config_file_not_found(self):
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = parse_config("dummy/path/config.json")
        self.assertEqual(result, DEFAULT_CONFIG)
