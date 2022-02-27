class Queue:
    def __init__(self, name=None) -> None:
        self._name = name
        self._client = None
        self._queue = None

    def _get_client(self):
        if not self._client:
            import boto3
            self._client = boto3.resource('sqs')
        return self._client

    def _get_queue(self):
        if not self._queue:
            self._queue = self._get_client().Queue(self._name)
        return self._queue

    def publish(self, body, group):
        self._get_queue().send_message(MessageBody=body, MessageGroupId=group)
