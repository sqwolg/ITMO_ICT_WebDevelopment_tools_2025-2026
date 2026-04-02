from enum import Enum
from datetime import datetime, timedelta
from typing import Union
import bcrypt
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends
from jose import JWTError, jwt
from models import User
from schemas import UserModel, UserCreateModel, UserUpdateModel
from settings import settings
from tortoise.queryset import QuerySet


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


class GetUserBy(Enum):
    id = 0
    username = 1


class UserService():
    @staticmethod
    async def _get(target: Union[str, int], get_by: GetUserBy, get_query: bool = False) -> User:
        if get_by is GetUserBy.id:
            user = User.filter(id=target).prefetch_related("todos")
        elif get_by is GetUserBy.username:
            user = User.filter(username=target).prefetch_related("todos")
        else:
            raise TypeError(f"Expected <GetUserBy> got {type(get_by)}")
        return await UserService._exists(user, get_query=get_query)

    @staticmethod
    async def _exists(user: QuerySet, get_query: bool = False) -> User:
        user_exists = await user.exists() if not not get_query else True
        if not get_query:
            user = await user.first()
        if not user or not user_exists:
            raise HTTPException(
                status_code=404,
                detail="Wrong username or user id specified"
            )
        return user

    @staticmethod
    async def get(user_id: int, get_query: bool = False) -> User:
        return await UserService._get(user_id, GetUserBy.id, get_query)

    @staticmethod
    async def get_by_username(username: str) -> User:
        return await UserService._get(username, get_by=GetUserBy.username)

    @staticmethod
    async def create(user_data: UserCreateModel) -> User:
        await UserService.validate_username(user_data.username)
        user_data.password = UserService.hash_password(user_data.password)
        user = await User.create(**user_data.dict())
        await user.fetch_related("todos")
        return user

    @staticmethod
    async def update(user_data: UserUpdateModel, user: UserModel) -> User:
        user_query = await UserService.get(user.id, get_query=True)
        if user_data.username != user.username:
            await UserService.validate_username(user_data.username)
        if user_data.password:
            user_data.password = UserService.hash_password(user_data.password)
        await user_query.update(**user_data.dict(exclude_unset=True))
        return await user_query.first()

    @staticmethod
    async def delete(user: UserModel) -> User:
        user = await UserService.get(user.id)
        user_query = await UserService.get(user.id, get_query=True)
        await user_query.delete()
        return user

    @staticmethod
    async def authenticate_user(username: str, password: str) -> Union[UserModel, bool]:
        user = await UserService.get_by_username(username)
        if not UserService.validate_password(password, user.password):
            return False
        return await UserModel.from_tortoise_orm(user)

    @staticmethod
    async def generate_access_token(user_id: int) -> str:
        now = datetime.utcnow()
        expires_in = now + timedelta(seconds=settings.jwt_token_expiration)
        payload = {"sub": str(user_id), "iat": now, "exp": expires_in}
        return jwt.encode(
            payload, settings.secret_key, algorithm=settings.jwt_algorithm)

    @staticmethod
    async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
        try:
            user_id = jwt.decode(
                token, settings.secret_key,
                algorithms=[settings.jwt_algorithm]
            ).get("sub", -1)
            user = await UserService.get(user_id)
        except JWTError:
            raise HTTPException(
                status_code=401,
                detail="Unable to validate credentials"
            )
        return await UserModel.from_tortoise_orm(user)

    @staticmethod
    async def validate_username(username) -> None:
        user_exists = await User.get(username=username).exists()
        if user_exists:
            raise HTTPException(
                status_code=409,
                detail=f"Username {username} is already taken"
            )

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=10)
        ).decode("utf-8")

    @staticmethod
    def validate_password(raw_password: str, hashed_password: str):
        return bcrypt.checkpw(
            raw_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
