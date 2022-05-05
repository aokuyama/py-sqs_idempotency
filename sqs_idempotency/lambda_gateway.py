from queue_storage import QueueStorage
import json
import unittest


class QueueLambdaGateway:
    def __init__(self, storage) -> None:
        self._storage = storage

    def _response(self, status, body):
        return {
            'isBase64Encoded': False,
            'statusCode': status,
            'headers': {},
            'body': body
        }

    def publish(self, event):
        if not "body" in event:
            return self._response(400, '{"message": "bad request"}')
        try:
            body = json.loads(event["body"])
        except json.JSONDecodeError:
            return self._response(400, '{"message": "bad request"}')
        return self._publish_msg(body)

    def _publish_msg(self, msg):
        if not "body" in msg:
            return self._response(400, '{"message": "undefined message body"}')
        if (not "group" in msg) or (not len(msg["group"])):
            return self._response(400, '{"message": "undefined message group"}')
        try:
            body = json.loads(msg["body"])
        except json.JSONDecodeError:
            body = msg["body"]
        r = self._storage.publish(body, msg["group"])
        if r["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return self._response(r["ResponseMetadata"]["HTTPStatusCode"], json.dumps(r))
        return self._response(200, '{"message": "OK"}')


class TestQueueLambdaGateway(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.queue = QueueLambdaGateway(self.QueueLambdaGatewayOk())

    def test_bodyがない(self):
        event = {"group": "hoge"}
        r = self.queue.publish(event)
        self.assertEqual(400, r["statusCode"])
        self.assertEqual('{"message": "bad request"}', r["body"])

    def test_json形式でないbody(self):
        event = {"body": "hoge"}
        r = self.queue.publish(event)
        self.assertEqual(400, r["statusCode"])
        self.assertEqual('{"message": "bad request"}', r["body"])

    def test_body内にgroupがない(self):
        event = {"body": json.dumps({"body": "hoge"})}
        r = self.queue.publish(event)
        self.assertEqual(400, r["statusCode"])
        self.assertEqual('{"message": "undefined message group"}', r["body"])
        event = {"body": json.dumps({"body": "hoge", "group": ""})}
        r = self.queue.publish(event)
        self.assertEqual(400, r["statusCode"])
        self.assertEqual('{"message": "undefined message group"}', r["body"])

    def test_body内にbodyがない(self):
        event = {"body": json.dumps({"group": "hoge"})}
        r = self.queue.publish(event)
        self.assertEqual(400, r["statusCode"])
        self.assertEqual('{"message": "undefined message body"}', r["body"])

    class QueueLambdaGatewayOk:
        def publish(self, body, group):
            return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    class QueueLambdaGatewayNg:
        def publish(self, body, group):
            return {"ResponseMetadata": {"HTTPStatusCode": 500}}

    def test_body内bodyが正常(self):
        event = {"body": json.dumps(
            {"body": json.dumps({"module": "hoge"}), "group": "hoge"})}
        r = self.queue.publish(event)
        self.assertEqual(200, r["statusCode"])
        self.assertEqual('{"message": "OK"}', r["body"])

    def test_body内bodyがjsonでなくても許容(self):
        event = {"body": json.dumps({"body": "hoge", "group": "hoge"})}
        r = self.queue.publish(event)
        self.assertEqual(200, r["statusCode"])
        self.assertEqual('{"message": "OK"}', r["body"])

    def test_body内bodyがjsonでなくても許容(self):
        event = {"body": json.dumps({"body": "hoge", "group": "hoge"})}
        r = self.queue.publish(event)
        self.assertEqual(200, r["statusCode"])
        self.assertEqual('{"message": "OK"}', r["body"])

    def test_キュー送信失敗(self):
        event = {"body": json.dumps({"body": "hoge", "group": "hoge"})}
        self.queue._storage = self.QueueLambdaGatewayNg()
        r = self.queue.publish(event)
        self.assertEqual(500, r["statusCode"])
        self.assertEqual(json.dumps(
            {"ResponseMetadata": {"HTTPStatusCode": 500}}), r["body"])


if __name__ == '__main__':
    unittest.main()
