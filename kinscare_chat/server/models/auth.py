from pydantic import BaseModel


class FbAuthCode(BaseModel):
    code: str
