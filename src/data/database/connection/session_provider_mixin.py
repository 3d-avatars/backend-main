from src.database.session import SessionManager
from src.constants import SESSION_DB_VAR_NAME


class SessionProviderMixin:
    @staticmethod
    def _session_provider(func):
        async def wrapped(*args, **kwargs):
            if kwargs.get(SESSION_DB_VAR_NAME) is None:
                async with SessionManager().get_session() as session:
                    kwargs[SESSION_DB_VAR_NAME] = session
                    return await func(*args, **kwargs)

            return await func(*args, **kwargs)

        return wrapped
