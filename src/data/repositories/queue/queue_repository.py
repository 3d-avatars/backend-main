from abc import ABC
from abc import abstractmethod


class QueueRepository(ABC):

    @abstractmethod
    async def push_message(self, message_body: str | bytes):
        raise NotImplementedError()
