from fastapi import HTTPException, status


SESSION_DB_VAR_NAME = '_session'

LIMIT_DB_STATEMENT = 'limit'
OFFSET_DB_STATEMENT = 'offset'

ORDER_BY_DB_STATEMENT = 'order_by'

DEFAULT_EXCHANGE = ''

CREDENTIAL_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

FORBIDDEN_EXCEPTION = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You can't change any task data",
)