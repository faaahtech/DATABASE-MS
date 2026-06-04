from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from controller.seed_controller import SeedController
from dtos.seed_dto import SeedBaseResponse
from repositories.postgres_conn import get_session

router = APIRouter(prefix="/seed", tags=["Seed"])
controller = SeedController()


@router.post("/base", response_model=SeedBaseResponse, status_code=status.HTTP_201_CREATED)
async def seed_base(
    session: AsyncSession = Depends(get_session),
) -> SeedBaseResponse:
    return await controller.seed_base(session=session)
