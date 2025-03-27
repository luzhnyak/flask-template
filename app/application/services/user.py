# from passlib.context import CryptContext
from app.infrastructure.repositories.user import UserRepository
from app.utils.exceptions import (
    BadRequestException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
)

# from app.models.user import User
# from app.repositories.user import UserRepository
# from app.schemas.user import (
#     SignUpRequest,
#     UserResponse,
#     UserUpdateRequest,
#     UsersListResponse,
# )
from sqlalchemy.ext.asyncio import AsyncSession

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, db: AsyncSession):
        self.user_repo = UserRepository(db)

    # def get_password_hash(self, password: str) -> str:
    #     return pwd_context.hash(password)

    async def create_user(self, user_data: SignUpRequest) -> UserResponse:
        user = await self.user_repo.find_one(email=user_data.email)
        if user:
            raise ConflictException("User with this email already exists")

        hashed_password = self.get_password_hash(user_data.password)
        new_user_data = {
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "email": user_data.email,
            "hashed_password": hashed_password,
        }
        new_user = await self.user_repo.add_one(new_user_data)

        return UserResponse.model_validate(new_user)

    async def get_users(self, skip: int = 0, limit: int = 10) -> UsersListResponse:
        total = await self.user_repo.count_all()
        page = (skip // limit) + 1
        users = await self.user_repo.find_all(skip=skip, limit=limit)
        return UsersListResponse(
            users=[UserResponse.model_validate(user) for user in users],
            total=total,
            page=page,
            per_page=limit,
        )

    async def get_user(self, user_id: int) -> UserResponse:
        user = await self.user_repo.find_one(id=user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")
        return UserResponse.model_validate(user)

    async def get_user_by_email(self, email: str) -> User:
        user = await self.user_repo.find_one(email=email)
        return user

    async def update_user(
        self, user_id: int, user_data: UserUpdateRequest, current_user_id: int
    ) -> UserResponse:
        if user_id != current_user_id:
            raise ForbiddenException("You can only update your own profile")

        user = await self.get_user(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        update_data = {}

        if user_data.first_name:
            update_data["first_name"] = user_data.first_name
        if user_data.last_name:
            update_data["last_name"] = user_data.last_name
        if user_data.password:
            update_data["hashed_password"] = self.get_password_hash(user_data.password)

        if not update_data:
            raise BadRequestException("No valid fields provided for update")

        user = await self.user_repo.edit_one(user_id, update_data)
        return UserResponse.model_validate(user)

    async def delete_user(self, user_id: int, current_user_id: int) -> UserResponse:
        if user_id != current_user_id:
            raise ForbiddenException("You can only delete your own account")

        user = await self.get_user(user_id)
        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        deleted_user = await self.user_repo.delete_one(user_id)
        return UserResponse.model_validate(deleted_user)
