"""API endpoints for Stinger service."""

# Import all routers to make them available
from . import check, health, metrics, rules

__all__ = ["check", "health", "rules", "metrics"]
