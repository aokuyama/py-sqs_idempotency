import unittest
from message import Message


class Messages:
    @classmethod
    def by_event(cls, event, max=10):
        msgs = Messages()
        msgs.parse_event(event, max)
        return msgs

    def __init__(self, msgs=None) -> None:
        self._msgs = msgs

    def get(self):
        return self._msgs

    def _check_error(self, max):
        msgs = self.get()
        if msgs is None:
            return
        if len(msgs) > max:
            raise RuntimeError

    def parse_event(self, event, max=10):
        self._msgs = Messages._parse_event(event)
        self._check_error(max)

    @classmethod
    def _parse_event(cls, event):
        if type(event) is not dict:
            raise AttributeError()
        messages = []
        if 'Records' not in event:
            return None
        for record in event['Records']:
            messages.append(Message(record))
        return messages


class TestMessages(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.messages = Messages()

    def test_初期化エラー(self):
        with self.assertRaises(AttributeError):
            self.messages.parse_event(None)

    def test_レコードがない(self):
        self.messages.parse_event({})
        self.assertIsNone(self.messages.get())

    def test_メッセージ取得(self):
        self.messages.parse_event({'Records': [{}, {}]}, 3)
        msgs = self.messages.get()
        self.assertEqual(2, len(msgs))

    def test_レコードが想定より多い場合エラー(self):
        with self.assertRaises(RuntimeError):
            self.messages.parse_event({'Records': [{}, {}, {}]}, 2)


if __name__ == '__main__':
    unittest.main()
