"""BDS Adapter for converting call recordings to vCon format."""

from .adapter import BDSAdapter
from .cli import main

__version__ = "0.1.0"
__all__ = ["BDSAdapter", "main"]