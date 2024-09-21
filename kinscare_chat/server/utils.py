import os

from fastapi import HTTPException, Header, status


def verify_secret_key(x_api_key: str = Header(None, alias="x-api-key")):
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key.")
    return x_api_key