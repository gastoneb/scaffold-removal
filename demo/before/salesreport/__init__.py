"""salesreport: total revenue per region from a sales file."""

from .aggregate import aggregate
from .config import Config
from .formatters import get_formatter
from .readers import get_reader

__all__ = ["Config", "aggregate", "get_formatter", "get_reader"]
