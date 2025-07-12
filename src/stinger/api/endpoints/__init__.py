"""API endpoints for Stinger service."""

# Import all routers to make them available
from . import check, health, rules, metrics

__all__ = ["check", "health", "rules", "metrics"]
