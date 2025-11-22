"""
TraeGuard: TRAE-powered Reliability & Responsible AI Lab for Digital Policies

A comprehensive privacy policy analysis platform that extends PrivyReveal with:
- Reliability Lab: Adversarial testing and robustness evaluation
- RAI Studio: Responsible AI explanations and impact analysis  
- Green Privacy: Environmental impact assessment and eco optimization
"""

__version__ = "1.0.0"
__author__ = "TraeGuard Team"

from . import reliability
from . import rai
from . import green
from . import ui
from . import utils

__all__ = ["reliability", "rai", "green", "ui", "utils"]