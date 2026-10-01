import contextlib
import importlib.util
import io
import json
import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch


def load_module(path):
    module_name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StoryScopeRegressionTests(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.sqlite3')
        os.close(self.db_fd)
        self.hide_module = load_module('/home/shalom/workspace/manhwa/manhwa-mirroring/server/hide_chapter.py')
        self.last_module = load_module('/home/shalom/workspace/manhwa/manhwa-mirroring/server/last_page.py')
        self.hide_module.DB_PATH = self.db_path
        self.last_module.DB_PATH = self.db_path

        conn = sqlite3.connect(self.db_path)
        self.hide_module.ensure_schema(conn)
        self.last_module.ensure_schema(conn)
        conn.close()

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def call_last_page_endpoint(self, values, method):
        class Form:
            def getfirst(self, name, default=''):
                return values.get(name, default)

        output = io.StringIO()
        with patch.object(self.last_module.cgi, 'FieldStorage', return_value=Form()), \
                patch.dict(os.environ, {'REQUEST_METHOD': method}), \
                contextlib.redirect_stdout(output):
            self.last_module.main()
        return json.loads(output.getvalue().split('\r\n\r\n', 1)[1])

    def test_story_scoped_hidden_and_last_page_state(self):
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter001', True)
        self.hide_module.set_hidden_state('Story Beta', 'Chapter001', False)

        self.assertEqual(self.hide_module.get_hidden_chapters('Story Alpha'), ['Chapter001'])
        self.assertEqual(self.hide_module.get_hidden_chapters('Story Beta'), [])

        self.last_module.set_last_page('Story Alpha', 'Chapter001', 12)
        self.last_module.set_last_page('Story Beta', 'Chapter001', 5)

        self.assertEqual(self.last_module.get_last_page('Story Alpha', 'Chapter001'), 12)
        self.assertEqual(self.last_module.get_last_page('Story Beta', 'Chapter001'), 5)

        self.last_module.set_first_page('Story Alpha', 'Chapter001', 3)
        self.last_module.set_first_page('Story Beta', 'Chapter001', 8)

        self.assertEqual(self.last_module.get_first_page('Story Alpha', 'Chapter001'), 3)
        self.assertEqual(self.last_module.get_first_page('Story Beta', 'Chapter001'), 8)
        self.assertEqual(self.last_module.get_last_page('Story Alpha', 'Chapter001'), 12)

        self.last_module.set_last_page('Story Alpha', 'Chapter001', 12)
        self.assertIsNone(self.last_module.get_last_page('Story Alpha', 'Chapter001'))
        self.assertEqual(self.last_module.get_first_page('Story Alpha', 'Chapter001'), 3)

        self.last_module.set_first_page('Story Alpha', 'Chapter001', 3)
        self.assertIsNone(self.last_module.get_first_page('Story Alpha', 'Chapter001'))
        self.assertEqual(self.last_module.get_first_page('Story Beta', 'Chapter001'), 8)

    def test_story_only_hidden_listing_is_valid(self):
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter001', True)
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter002', True)
        self.hide_module.set_hidden_state('Story Beta', 'Chapter001', True)

        self.assertEqual(self.hide_module.get_hidden_chapters('Story Alpha'), ['Chapter001', 'Chapter002'])

    def test_hidden_state_does_not_create_zero_last_page_marker(self):
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter001', True)
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter001', False)

        self.assertIsNone(self.last_module.get_last_page('Story Alpha', 'Chapter001'))

    def test_existing_chapter_state_schema_gains_first_page_column(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('DROP TABLE chapter_limits')
        conn.execute(
            'CREATE TABLE chapter_limits ('
            'story TEXT NOT NULL, chapter TEXT NOT NULL, last_page INTEGER, '
            'hidden INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(story, chapter))'
        )
        conn.execute(
            'INSERT INTO chapter_limits(story, chapter, last_page) VALUES(?, ?, ?)',
            ('Story Alpha', 'Chapter001', 14),
        )

        self.last_module.ensure_schema(conn)
        self.hide_module.ensure_schema(conn)
        columns = {row[1] for row in conn.execute('PRAGMA table_info(chapter_limits)')}
        conn.commit()
        conn.close()

        self.assertIn('first_page', columns)
        self.assertEqual(self.last_module.get_last_page('Story Alpha', 'Chapter001'), 14)
        self.last_module.set_first_page('Story Alpha', 'Chapter001', 4)
        self.assertEqual(self.last_module.get_first_page('Story Alpha', 'Chapter001'), 4)

    def test_endpoint_reads_and_toggles_first_page_without_changing_last_page(self):
        self.last_module.set_last_page('Story Alpha', 'Chapter001', 15)
        request = {'story': 'Story Alpha', 'chapter': 'Chapter001', 'page': '4', 'marker': 'first_page'}

        set_response = self.call_last_page_endpoint(request, 'POST')
        get_response = self.call_last_page_endpoint(
            {'story': 'Story Alpha', 'chapter': 'Chapter001'},
            'GET',
        )
        clear_response = self.call_last_page_endpoint(request, 'POST')

        self.assertEqual(set_response['first_page'], 4)
        self.assertEqual(get_response['first_page'], 4)
        self.assertEqual(get_response['last_page'], 15)
        self.assertIsNone(clear_response['first_page'])
        self.assertEqual(self.last_module.get_last_page('Story Alpha', 'Chapter001'), 15)


if __name__ == '__main__':
    unittest.main()
