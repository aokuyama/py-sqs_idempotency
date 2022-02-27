import unittest
from message import Message


class Deduplication:
    def __init__(self, table_name=None) -> None:
        self._table_name = table_name
        self._dynamodb = None

    def _get_dynamodb(self):
        if not self._dynamodb:
            import boto3
            self._dynamodb = boto3.client('dynamodb')
        return self._dynamodb

    def _key(self) -> str:
        return 'deduplication_id'

    def lock(self, dedup_id: str) -> bool:
        import botocore.exceptions
        try:
            self._put(dedup_id)
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                return False
            else:
                raise e

    def _put(self, dedup_id: str):
        return self._get_dynamodb().put_item(
            TableName=self._table_name,
            Item={self._key(): {'S': dedup_id}},
            Expected={self._key(): {'Exists': False}}
        )

    def lock_msg(self, msg: Message) -> bool:
        return self.lock(msg.get_deduplication_id())

    def unlock(self, dedup_id: str) -> None:
        self._get_dynamodb().delete_item(
            TableName=self._table_name,
            Key={self._key(): {'S': dedup_id}}
        )

    def unlock_msg(self, msg: Message) -> bool:
        return self.unlock(msg.get_deduplication_id())


class TestDeduplication(unittest.TestCase):
    maxDiff = None

    class SuccessTest(Deduplication):
        def _put(self, dedup_id: str):
            pass

    class FailTest(Deduplication):
        def _put(self, dedup_id: str):
            class ClientErrorMock(botocore.exceptions.ClientError):
                def __init__(self):
                    self.response = {}
                    self.response['Error'] = {}
                    self.response['Error']['Code'] = 'ConditionalCheckFailedException'
            raise ClientErrorMock()

    class RaiseTest1(Deduplication):
        def _put(self, dedup_id: str):
            class ClientErrorMock(botocore.exceptions.ClientError):
                def __init__(self):
                    self.response = {}
                    self.response['Error'] = {}
                    self.response['Error']['Code'] = 'a'
            raise ClientErrorMock()

    class RaiseTest2(Deduplication):
        def _put(self, dedup_id: str):
            raise botocore.exceptions.NoRegionError()

    class RaiseTest3(Deduplication):
        def _put(self, dedup_id: str):
            raise AttributeError

    def setUp(self):
        self.dedup = Deduplication()

    def test_lockに成功したらtrue(self):
        self.assertTrue(self.SuccessTest().lock('abc'))

    def test_lockに失敗したらfalse(self):
        self.assertFalse(self.FailTest().lock('abc'))

    def test_それ以外は例外を投げる(self):
        with self.assertRaises(botocore.exceptions.ClientError):
            self.RaiseTest1().lock('abc')
        with self.assertRaises(botocore.exceptions.NoRegionError):
            self.RaiseTest2().lock('abc')
        with self.assertRaises(AttributeError):
            self.RaiseTest3().lock('abc')


if __name__ == '__main__':
    import botocore.exceptions
    unittest.main()
