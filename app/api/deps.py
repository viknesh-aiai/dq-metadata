from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.repositories.metadata_repo import MetadataRepository
from app.services.enrichment import EnrichmentService
from app.services.context_builder import ContextBuilderService


async def get_metadata_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)]
) -> MetadataRepository:
    return MetadataRepository(session)


async def get_enrichment_service() -> EnrichmentService:
    # Service is stateless/singleton-ish as it just reads config
    return EnrichmentService()


async def get_context_builder_service(
    repo: Annotated[MetadataRepository, Depends(get_metadata_repository)],
    enrichment: Annotated[EnrichmentService, Depends(get_enrichment_service)]
) -> ContextBuilderService:
    return ContextBuilderService(repo, enrichment)
