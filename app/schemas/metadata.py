from typing import Dict, List
from pydantic import BaseModel, Field, field_validator


class AppMetadataResponse(BaseModel):
    """
    Metadata Context with Natural Language Summaries.
    Structure: App -> Schema -> Table -> "Description String"
    """
    app_name: str
    data_dictionary: Dict[str, Dict[str, str]] = Field(default_factory=dict)


class MultiAppMetadataRequest(BaseModel):
    """Request model for multi-app metadata query."""
    app_names: List[str] = Field(
        ...,
        min_length=1,
        max_length=3,
        description="List of application names (1-3 apps)"
    )
    schema: str | None = Field(None, description="Optional schema filter")

    @field_validator('app_names')
    @classmethod
    def validate_unique_apps(cls, v: List[str]) -> List[str]:
        if len(v) != len(set(v)):
            raise ValueError("Duplicate app names are not allowed")
        return v


class MultiAppMetadataResponse(BaseModel):
    """Response containing metadata for multiple applications."""
    apps: List[AppMetadataResponse] = Field(default_factory=list)
    total_apps: int = 0
