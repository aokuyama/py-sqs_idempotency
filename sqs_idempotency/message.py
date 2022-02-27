import json
import unittest


class Message:
    def __init__(self, record=None) -> None:
        self.record = record

    def body_raw(self):
        return self.record['body']

    def data(self):
        return json.loads(self.body_raw())

    def get_deduplication_id(self):
        return self.record['attributes']['MessageDeduplicationId']

class TestMessage(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.message = Message()

    def test_body内jsonを展開(self):
        self.message.record = {'body': '{"name":123}'}
        self.assertEqual('{"name":123}', self.message.body_raw())
        self.assertEqual({"name": 123}, self.message.data())


if __name__ == '__main__':
    unittest.main()
