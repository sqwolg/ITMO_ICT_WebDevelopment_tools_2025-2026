from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from todo_app.schemas import UserModel, UserCreateModel, UserUpdateModel, UpdateUserPassword
from todo_app.services import UserService


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


@router.get("/", response_model=list[UserModel])
async def get_users():
    return await UserService.get_all()


@router.post("/", response_model=UserModel)
async def create_user(data: UserCreateModel):
    return await UserService.create(data)


@router.post("/change-password", response_model=UserModel)
async def change_password(
    data: UpdateUserPassword,
    user: UserModel = Depends(UserService.get_current_user)
):
    user_model = await UserService.authenticate_user(
        username=user.username,
        password=data.old_password,
    )
    if not user_model:
        raise HTTPException(status_code=409, detail="Old password is incorrect")

    await UserService.change_password(
        user_id=user.id,
        new_password=data.new_password,
    )

    return user_model


@router.put("/me", response_model=UserModel)
async def update_user(
    data: UserUpdateModel,
    user: UserModel = Depends(UserService.get_current_user)
):
    return await UserService.update(data, user)


@router.delete("/me", response_model=UserModel)
async def delete_user(user: UserModel = Depends(UserService.get_current_user)):
    return await UserService.delete(user)
