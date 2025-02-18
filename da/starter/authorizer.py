from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

import jwt
from fastapi import Depends, FastAPI, HTTPException, status, requests
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel
from da.logger import logger

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "f98108dba0d2df6c864c608bea9dc347972c875b382295df7887a7229a9aa776"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Union[int, None] = None
    username: Union[str, None] = None

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: TokenData, expires_delta: Union[timedelta, None] = None):
    to_encode = dict(data)
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=365)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_token_data(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(
            username = payload.get("username"),
            user_id = payload.get("user_id")
            )
        return token_data
    except InvalidTokenError as e:
        logger.exception(e)
        return TokenData()
