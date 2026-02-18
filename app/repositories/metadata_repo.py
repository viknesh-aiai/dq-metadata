from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metadata import MetadataColumn
from app.core.exceptions import DatabaseError


class MetadataRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_app_columns(
            self, app_name: str, schema: Optional[str] = None
    ) -> List[MetadataColumn]:
        """
        Fetch all columns for an application, optionally filtered by schema.
        """
        try:
            query = select(MetadataColumn).where(
                MetadataColumn.app_name == app_name
            )

            if schema:
                query = query.where(MetadataColumn.table_schema == schema)

            # Order by table for easier grouping later
            query = query.order_by(MetadataColumn.table_schema, MetadataColumn.table_name)

            result = await self.session.execute(query)
            columns = result.scalars().all()
            return list(columns)
        except Exception as e:
            raise DatabaseError(f"Error fetching metadata for app {app_name}: {str(e)}") from e