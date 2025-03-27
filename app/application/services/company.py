from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)
from app.repositories.company import CompanyRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.company import (
    CompaniesListResponse,
    CompanyCreateRequest,
    CompanyResponse,
    CompanyUpdateRequest,
)


class CompanyService:
    def __init__(self, db: AsyncSession):
        self.company_repo = CompanyRepository(db)

    async def create_company(
        self, company_data: CompanyCreateRequest, current_user_id: int
    ) -> CompanyResponse:

        new_company_data = {
            "name": company_data.name,
            "description": company_data.description,
            "visibility": False,
            "owner_id": current_user_id,
        }

        new_company = await self.company_repo.add_one(new_company_data)

        return CompanyResponse.model_validate(new_company)

    async def get_companies(
        self, skip: int = 0, limit: int = 10
    ) -> CompaniesListResponse:
        total = await self.company_repo.count_all()
        page = (skip // limit) + 1
        companies = await self.company_repo.find_all(skip=skip, limit=limit)
        return CompaniesListResponse(
            items=[CompanyResponse.model_validate(company) for company in companies],
            total=total,
            page=page,
            per_page=limit,
        )

    async def get_company(self, company_id: int) -> CompanyResponse:
        company = await self.company_repo.find_one(id=company_id)
        if not company:
            raise NotFoundException(f"Company with id {company_id} not found")
        return CompanyResponse.model_validate(company)

    async def update_company(
        self, company_id: int, company_data: CompanyUpdateRequest, current_user_id: int
    ) -> CompanyResponse:
        company = await self.get_company(company_id)

        if not company:
            raise NotFoundException(f"Company with id {company_id} not found")

        if company.owner_id != current_user_id:
            raise ForbiddenException("You can only update your own company")

        update_data = {
            "name": company_data.name,
            "description": company_data.description,
        }

        if not update_data:
            raise BadRequestException("No valid fields provided for update")

        company = await self.company_repo.edit_one(company_id, update_data)
        return CompanyResponse.model_validate(company)

    async def update_company_visibility(
        self, company_id: int, visibility: bool, current_user_id: int
    ) -> CompanyResponse:
        company = await self.get_company(company_id)

        if not company:
            raise NotFoundException(f"Company with id {company_id} not found")

        if company.owner_id != current_user_id:
            raise ForbiddenException("You can only update your own company")

        update_data = {"visibility": visibility}

        company = await self.company_repo.edit_one(company_id, update_data)
        return CompanyResponse.model_validate(company)

    async def delete_company(
        self, company_id: int, current_user_id: int
    ) -> CompanyResponse:
        company = await self.get_company(company_id)

        if not company:
            raise NotFoundException(f"Company with id {company_id} not found")

        if company.owner_id != current_user_id:
            raise ForbiddenException("You can only delete your own company")

        deleted_company = await self.company_repo.delete_one(company_id)
        return CompanyResponse.model_validate(deleted_company)
