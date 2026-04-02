from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UserModel, UserCreateModel, UserUpdateModel
from services import UserService


router = APIRouter(prefix="/users")


@router.post("/token")
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await UserService.authenticate_user(
        form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Wrong username or password"
        )
    access_token = await UserService.generate_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserModel)
async def get_user(user: UserModel = Depends(UserService.get_current_user)):
    return user


@router.post("/", response_model=UserModel)
async def create_user(data: UserCreateModel):
    return await UserService.create(data)


@router.put("/me", response_model=UserModel)
async def update_user(
    data: UserUpdateModel,
    user: UserModel = Depends(UserService.get_current_user)
):
    return await UserService.update(data, user)


@router.delete("/me", response_model=UserModel)
async def delete_user(user: UserModel = Depends(UserService.get_current_user)):
    return await UserService.delete(user)
