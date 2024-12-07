from abc import ABC, abstractmethod


class QueueRepository(ABC):

    @abstractmethod
    async def push_message(self, message_body: str | bytes):
        raise NotImplementedError()
