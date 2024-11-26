from ..repositories.base_repository import AbstractRepository


class BaseService:
    def __init__(self, repository: AbstractRepository) -> None:
        self.repository: AbstractRepository = repository

    async def create(self, *args, **kwargs):
        ...

    async def update(self,  *args, **kwargs):
        ...

    async def delete(self,  *args, **kwargs):
        ...

    async def get(self,  *args, **kwargs):
        ...

    async def get_single(self, *args, **kwargs):
        ...
