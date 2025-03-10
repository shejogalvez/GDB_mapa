from fastapi import APIRouter, Depends, HTTPException, status, Form 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from passlib.pwd import genword
from models import User, UserInDB, RoleEnum, UserForm
from typing import List, Optional, Annotated
from jose import jwt, JWTError
from datetime import timedelta, datetime
import os
import db

router = APIRouter()

SECRET = os.getenv("API_SECRET")
# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper functions to authenticate and verify users
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    user = db.get_user(username)
    # if username not in users_db: # for use of test db
    #     return None
    # user = users_db[username]
    if user:
        return UserInDB(**user)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or not verify_password(password + user.salt, user.hashed_password):
        return False
    return user

# Define a dependency that checks if the user has certain permissions
def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        user = decode_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError as e:
        print("JWT.Exception: ", e)
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"could not validate user",
        )
        

def get_admin_permission_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role == RoleEnum.admin:
        return current_user
    raise HTTPException(status_code=403, detail="Permission denied: only administrator can access")

def get_read_permission_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role in [RoleEnum.admin, RoleEnum.reader, RoleEnum.writer]:
        return current_user
    raise HTTPException(status_code=403, detail="Permission denied: No read access")

def get_write_permission_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.role in [RoleEnum.admin, RoleEnum.writer]:
        return current_user
    raise HTTPException(status_code=403, detail="Permission denied: No write access")

def enconde_token(payload: dict, expires_delta: timedelta) -> str:
    payload.update({"exp": datetime.now() + expires_delta})
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    return token

def decode_token(token: str):
    data = jwt.decode(token, SECRET, algorithms=["HS256"])
    user = get_user(data["username"])
    return user

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = enconde_token({"username": user.username}, expires_delta= timedelta(minutes=300))
    return {"access_token": token, "token_type": "bearer"}

@router.post("/user", dependencies=[Depends(get_admin_permission_user)])
async def add_user(user: Annotated[UserForm, Form()]):
    salt = genword(length=15, charset="ascii_72")
    hashed_password = pwd_context.hash(user.password + salt)
    db.create_user(user.username, hashed_password, salt, user.role.value)
    return {"username": user.username}

## TEST ROUTES
# Open route, anyone can access
@router.get("/user")
async def root(username: str):
    return get_user(username)

# Only users with read permissions can access this route
@router.get("/user/read-data", dependencies=[Depends(get_read_permission_user)])
async def read_data():
    return {"data": "This is read-only data"}

# Only users with write permissions can access this route
@router.post("/user/write-data", dependencies=[Depends(get_write_permission_user)])
async def write_data():
    return {"message": "Data written successfully"}

# Admin-only route
@router.get("/user/admin", dependencies=[Depends(get_admin_permission_user)])
async def admin_panel():
    return {"message": "Welcome to the admin panel"}
