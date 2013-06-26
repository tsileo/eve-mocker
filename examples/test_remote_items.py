from eve_mocker import EveMocker
import unittest
from remote_items import RemoteItems, API_URL


class TestRemoteItems(unittest.TestCase):
    def testGetLatestItems(self):
        items = [{"_id": "fakeid", "content": "my content"},
                 {"_id": "fakeid2", "content": "another_content"}]
        with EveMocker(API_URL) as eve_mocker:
            # We feed EveMocker DB with some items
            eve_mocker.set_resource("items", items)

            remote_items = RemoteItems()
            latest_items = remote_items.get_latest()

            self.assertEqual(sorted(latest_items), sorted(items))

if __name__ == '__main__':
    unittest.main()
