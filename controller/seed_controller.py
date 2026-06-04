from sqlmodel.ext.asyncio.session import AsyncSession

from dtos.seed_dto import SeedBaseResponse
from services.seed_service import SeedService


class SeedController:
    def __init__(self) -> None:
        self.service = SeedService()

    async def seed_base(self, session: AsyncSession) -> SeedBaseResponse:
        return await self.service.seed_base(session=session)
