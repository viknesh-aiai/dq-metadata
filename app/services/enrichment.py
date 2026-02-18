from typing import List, Optional
from app.models.metadata import MetadataColumn
from app.core.heuristics import get_heuristics


class EnrichmentService:
    def __init__(self):
        self.heuristics = get_heuristics()

    def normalize_datatype(self, raw_type: str) -> str:
        """
        Normalizes database specific types to a simplified set.
        """
        raw_lower = raw_type.lower()
        if "int" in raw_lower or "serial" in raw_lower or "number" in raw_lower:
            return "integer"
        if "char" in raw_lower or "text" in raw_lower or "string" in raw_lower:
            return "string"
        if "float" in raw_lower or "double" in raw_lower or "decimal" in raw_lower or "numeric" in raw_lower:
            return "float"
        if "bool" in raw_lower:
            return "boolean"
        if "date" in raw_lower or "time" in raw_lower:
            return "datetime"
        if "json" in raw_lower:
            return "json"
        if "uuid" in raw_lower:
            return "uuid"
        return "unknown"

    def detect_sensitivity(self, column_name: str) -> Optional[str]:
        """
        Checks if the column name matches any PII keywords.
        """
        name_lower = column_name.lower()
        for keyword in self.heuristics.pii_keywords:
            if keyword in name_lower:
                return "PII"
        return None

    def is_candidate_key(self, column_name: str) -> bool:
        """
        Heuristic check for potential primary/candidate keys.
        """
        name_lower = column_name.lower()
        for pattern in self.heuristics.candidate_key_patterns:
            if pattern in name_lower:
                return True
        return False

    def is_temporal(self, column_name: str, data_type: str) -> bool:
        """
        Checks if column is time-related based on name or type.
        """
        # Check type first
        norm_type = self.normalize_datatype(data_type)
        if norm_type == "datetime":
            return True

        # Check name pattern
        name_lower = column_name.lower()
        for pattern in self.heuristics.temporal_patterns:
            if pattern in name_lower:
                return True
        return False

    def determine_semantic_role(self, column_name: str, data_type: str) -> str:
        """
        Assigns a broad semantic role to the column.
        """
        if self.is_candidate_key(column_name):
            return "key"
        if self.is_temporal(column_name, data_type):
            return "temporal"
        
        # Fallback based on type
        norm_type = self.normalize_datatype(data_type)
        if norm_type in ("integer", "float"):
            return "measure"
        
        return "attribute"
