__all__ = ["start_router", "stats_router", "language_router"]

from .language import router as language_router
from .start import router as start_router
from .stats import router as stats_router
