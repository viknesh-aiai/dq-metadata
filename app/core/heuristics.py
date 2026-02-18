from pathlib import Path
from typing import Dict, List, Any
import yaml
from pydantic import BaseModel

from app.core.exceptions import HeuristicsError


class HeuristicsConfig(BaseModel):
    pii_keywords: List[str]
    candidate_key_patterns: List[str]
    temporal_patterns: List[str]
    high_cardinality_threshold: float
    low_cardinality_threshold: float


class HeuristicsLoader:
    _instance = None
    _config: HeuristicsConfig = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = HeuristicsLoader()
        return cls._instance

    def __init__(self):
        self._load_config()

    def _load_config(self):
        try:
            # Assuming config is at the root level relative to app execution
            # Adjust path as necessary based on deployment
            config_path = Path("config/heuristics.yaml")
            if not config_path.exists():
                # Fallback for running from inside app/ folder or tests
                config_path = Path("../config/heuristics.yaml")
            
            if not config_path.exists():
                raise HeuristicsError(f"Heuristics config file not found at {config_path.absolute()}")

            with open(config_path, "r") as f:
                raw_config = yaml.safe_load(f)
                self._config = HeuristicsConfig(**raw_config)
                
        except Exception as e:
            raise HeuristicsError(f"Failed to load heuristics: {str(e)}") from e

    @property
    def config(self) -> HeuristicsConfig:
        if self._config is None:
            self._load_config()
        return self._config

# Global accessor
def get_heuristics() -> HeuristicsConfig:
    return HeuristicsLoader.get_instance().config
