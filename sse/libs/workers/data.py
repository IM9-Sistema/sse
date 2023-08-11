from libs.structures import Worker
from libs.consumer import consume_from_topic
import pyding



class DataGather(Worker):
    async def work(self):
        while True:
            async for message, id in consume_from_topic('positions'):
                pyding.call('position.message', message=message, id=id, tracker_id=message['rastreador']['id'], **message)
                pyding.call('position.message', message=message, id=id, tracker_id=6952, **message)

    @classmethod
    def begin(cls):
        instance = cls()
        instance.start()
        return instance
    