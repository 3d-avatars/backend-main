from fastapi import HTTPException
from fastapi import status

SESSION_DB_VAR_NAME = 'session'

DEFAULT_EXCHANGE = ''

CREDENTIAL_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

FORBIDDEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You can't change any tasks data",
)