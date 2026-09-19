import importlib.util
import os
import sqlite3
import tempfile
import unittest


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

    def test_story_scoped_hidden_and_last_page_state(self):
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter001', True)
        self.hide_module.set_hidden_state('Story Beta', 'Chapter001', False)

        self.assertEqual(self.hide_module.get_hidden_chapters('Story Alpha'), ['Chapter001'])
        self.assertEqual(self.hide_module.get_hidden_chapters('Story Beta'), [])

        self.last_module.set_last_page('Story Alpha', 'Chapter001', 12)
        self.last_module.set_last_page('Story Beta', 'Chapter001', 5)

        self.assertEqual(self.last_module.get_last_page('Story Alpha', 'Chapter001'), 12)
        self.assertEqual(self.last_module.get_last_page('Story Beta', 'Chapter001'), 5)

        self.last_module.set_last_page('Story Alpha', 'Chapter001', 12)
        self.assertIsNone(self.last_module.get_last_page('Story Alpha', 'Chapter001'))

    def test_story_only_hidden_listing_is_valid(self):
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter001', True)
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter002', True)
        self.hide_module.set_hidden_state('Story Beta', 'Chapter001', True)

        self.assertEqual(self.hide_module.get_hidden_chapters('Story Alpha'), ['Chapter001', 'Chapter002'])

    def test_hidden_state_does_not_create_zero_last_page_marker(self):
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter001', True)
        self.hide_module.set_hidden_state('Story Alpha', 'Chapter001', False)

        self.assertIsNone(self.last_module.get_last_page('Story Alpha', 'Chapter001'))


if __name__ == '__main__':
    unittest.main()
