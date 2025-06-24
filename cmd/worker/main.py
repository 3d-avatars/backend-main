import asyncio

from worker import get_worker


async def main():
    w = get_worker()
    await w.run()

if __name__ == '__main__':
    asyncio.run(main())
