"""
Green Privacy: Environmental impact assessment and eco optimization for privacy analysis
"""

# Import only available submodules to avoid deployment errors
try:
    from . import footprint
except Exception:
    footprint = None

# Optional modules (may not exist in minimal deployments)
try:
    from . import carbon
except Exception:
    carbon = None

try:
    from . import eco_mode
except Exception:
    eco_mode = None

__all__ = [name for name, mod in {
    "footprint": footprint,
    "carbon": carbon,
    "eco_mode": eco_mode
}.items() if mod is not None]