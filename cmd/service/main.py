import asyncio
import logging

import uvicorn
from app.app import app, prune_application_dependencies

from config import get_settings


async def main():
    settings = get_settings()

    try:
        uvicorn.run(
            "cmd.service.main:app",
            host=settings.APP_HOST,
            port=settings.APP_PORT,
            reload=True,
            reload_dirs=["src", "app", "config"],
            log_config="log_conf.yaml",
            log_level=logging.INFO,
            proxy_headers=True
        )
    except Exception:
        await prune_application_dependencies()
        raise


if __name__ == "__main__":
    asyncio.run(main())
