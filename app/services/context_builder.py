from typing import List, Optional, Dict

from app.repositories.metadata_repo import MetadataRepository
from app.services.enrichment import EnrichmentService
from app.schemas.metadata import AppMetadataResponse
from app.models.metadata import MetadataColumn


class ContextBuilderService:
    def __init__(self, repo: MetadataRepository, enrichment_service: EnrichmentService):
        self.repo = repo
        self.enrichment = enrichment_service

    async def build_multi_app_context(
            self, app_names: List[str], schema: Optional[str] = None
    ) -> List[AppMetadataResponse]:
        """Build context for multiple applications."""
        results = []
        for app_name in app_names:
            app_context = await self.build_app_context(app_name, schema)
            results.append(app_context)
        return results

    async def build_app_context(self, app_name: str, schema: Optional[str] = None) -> AppMetadataResponse:
        raw_columns = await self.repo.get_app_columns(app_name, schema)

        # Group by schema -> table
        content: Dict[str, Dict[str, List[MetadataColumn]]] = {}
        for col in raw_columns:
            # Handle None schema by using a default value
            sch = col.table_schema if col.table_schema is not None else "default"
            tbl = col.table_name if col.table_name is not None else "unknown"

            if sch not in content:
                content[sch] = {}
            if tbl not in content[sch]:
                content[sch][tbl] = []
            content[sch][tbl].append(col)

        # Generate Summaries
        final_dict: Dict[str, Dict[str, str]] = {}

        for sch, tables in content.items():
            final_dict[sch] = {}
            for tbl, cols in tables.items():
                final_dict[sch][tbl] = self._generate_nl_summary(tbl, cols)

        return AppMetadataResponse(
            app_name=app_name,
            data_dictionary=final_dict
        )

    def _generate_nl_summary(self, table_name: str, columns: List[MetadataColumn]) -> str:
        """
        Generates: "Table X contains N columns: col1, col2. Primary candidate fields: A. Likely PII: B..."
        """
        count = len(columns)

        # Extract column names using a list comprehension
        all_column_names = [col.column_name for col in columns]
        col_list_str = ", ".join(all_column_names)

        primary_keys = []
        pii_fields = []
        temporal_fields = []
        numeric_fields = []

        for col in columns:
            name = col.column_name
            dtype = col.data_type.lower() if col.data_type else ""

            # Use enrichment service for robust detection
            is_key = self.enrichment.is_candidate_key(name)
            sensitivity = self.enrichment.detect_sensitivity(name)
            is_temporal = self.enrichment.is_temporal(name, dtype)

            is_numeric = any(x in dtype for x in ['int', 'decimal', 'float', 'numeric', 'double'])

            if is_key:
                primary_keys.append(name)
            if sensitivity:
                pii_fields.append(f"{name}({sensitivity})")
            if is_temporal:
                temporal_fields.append(name)
            if is_numeric and not is_key:
                numeric_fields.append(name)

        # Sentence Construction
        parts = [f"Table {table_name} contains {count} columns: {col_list_str}."]

        if primary_keys:
            parts.append(f"Primary candidate fields: {', '.join(primary_keys)}.")

        if pii_fields:
            parts.append(f"Likely PII fields: {', '.join(pii_fields)}.")

        if temporal_fields:
            parts.append(f"Temporal fields: {', '.join(temporal_fields)}.")

        return " ".join(parts)
