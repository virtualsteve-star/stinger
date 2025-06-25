class GuardrailsError(Exception):
    """Base exception for guardrails framework."""
    pass

class ConfigurationError(GuardrailsError):
    """Raised when configuration is invalid."""
    pass

class FilterError(GuardrailsError):
    """Raised when a filter encounters an error."""
    pass

class PipelineError(GuardrailsError):
    """Raised when pipeline processing fails."""
    pass 