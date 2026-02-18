from typing import Annotated, Optional, List

from fastapi import APIRouter, Depends, Query, HTTPException

from app.api.deps import get_context_builder_service
from app.services.context_builder import ContextBuilderService
from app.schemas.metadata import AppMetadataResponse, MultiAppMetadataResponse
from app.core.logging import logger

router = APIRouter()


@router.get("/context", response_model=AppMetadataResponse)
async def get_metadata_context(
        app_name: str = Query(..., description="Name of the application owning the data"),
        schema: Optional[str] = Query(None, description="Filter by database schema name"),
        service: Annotated[ContextBuilderService, Depends(get_context_builder_service)] = None
):
    """
    Get AI-ready metadata context with Natural Language summaries.
    """
    logger.info("Fetching metadata context for app", app_name=app_name, schema=schema)

    return await service.build_app_context(
        app_name=app_name,
        schema=schema
    )


@router.get("/context/multi", response_model=MultiAppMetadataResponse)
async def get_multi_app_metadata_context(
        app_name_1: str = Query(..., description="First application name (required)"),
        app_name_2: Optional[str] = Query(None, description="Second application name (optional)"),
        app_name_3: Optional[str] = Query(None, description="Third application name (optional)"),
        service: Annotated[ContextBuilderService, Depends(get_context_builder_service)] = None
):
    """
    Get AI-ready metadata context for multiple applications (1-3 apps).
    Returns combined metadata suitable for downstream services.
    """
    # Build list of app names, filtering out None values
    app_names = [name for name in [app_name_1, app_name_2, app_name_3] if name]

    # Check for duplicates
    if len(app_names) != len(set(app_names)):
        raise HTTPException(status_code=400, detail="Duplicate app names are not allowed")

    logger.info("Fetching metadata context for multiple apps", app_names=app_names)

    apps = await service.build_multi_app_context(
        app_names=app_names,
        schema=None
    )

    return MultiAppMetadataResponse(
        apps=apps,
        total_apps=len(apps)
    )
