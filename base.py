"""
Base classes and utilities for TraeGuard modules
"""
import time
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Base class for all analysis results"""
    timestamp: float
    module: str
    status: str  # 'success', 'error', 'warning'
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

@dataclass
class ReliabilityResult(AnalysisResult):
    """Results from reliability analysis"""
    robustness_score: float
    confidence_stability: float
    adversarial_examples: List[Dict[str, Any]]
    cross_model_agreement: Optional[float] = None

@dataclass
class RAIResult(AnalysisResult):
    """Results from RAI analysis"""
    explanation: str
    beneficiary_analysis: Dict[str, Any]
    vulnerable_impact: Dict[str, str]
    fairness_score: float
    external_consensus: Optional[Dict[str, Any]] = None

@dataclass
class GreenResult(AnalysisResult):
    """Results from green privacy analysis"""
    carbon_footprint: float
    data_footprint_score: float
    eco_mode_recommendations: List[str]
    environmental_impact_level: str  # 'low', 'medium', 'high'

class BaseAnalyzer(ABC):
    """Abstract base class for all TraeGuard analyzers"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.logger = logging.getLogger(f"traeguard.{name}")
        
    @abstractmethod
    def analyze(self, text: str, **kwargs) -> AnalysisResult:
        """Main analysis method to be implemented by subclasses"""
        pass
    
    def validate_input(self, text: str) -> bool:
        """Validate input text"""
        if not text or not isinstance(text, str):
            return False
        if len(text.strip()) < 10:  # Minimum meaningful text length
            return False
        return True
    
    def log_analysis_start(self, text: str, **kwargs):
        """Log analysis start"""
        self.logger.info(f"Starting {self.name} analysis for text of length {len(text)}")
        
    def log_analysis_complete(self, duration: float, status: str):
        """Log analysis completion"""
        self.logger.info(f"Completed {self.name} analysis in {duration:.2f}s with status: {status}")

class MetricsCollector:
    """Utility class for collecting and aggregating metrics"""
    
    def __init__(self):
        self.metrics = {}
        
    def record_metric(self, name: str, value: Any, metadata: Dict[str, Any] = None):
        """Record a metric with optional metadata"""
        if name not in self.metrics:
            self.metrics[name] = []
        
        metric_entry = {
            "timestamp": time.time(),
            "value": value,
            "metadata": metadata or {}
        }
        self.metrics[name].append(metric_entry)
    
    def get_metric_stats(self, name: str) -> Dict[str, Any]:
        """Get statistics for a metric"""
        if name not in self.metrics or not self.metrics[name]:
            return {}
        
        values = [entry["value"] for entry in self.metrics[name] if isinstance(entry["value"], (int, float))]
        if not values:
            return {}
        
        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "latest": values[-1]
        }
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics"""
        return {
            name: self.get_metric_stats(name) 
            for name in self.metrics.keys()
        }

class CacheManager:
    """Simple in-memory cache for analysis results"""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                return entry["value"]
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: Any):
        """Set item in cache with TTL"""
        # Simple LRU eviction
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]["timestamp"])
            del self.cache[oldest_key]
        
        self.cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()

def create_cache_key(text: str, analysis_type: str, **kwargs) -> str:
    """Create a cache key for analysis results"""
    # Simple hash-based key (could be improved with more sophisticated hashing)
    text_hash = hash(text.strip().lower())
    kwargs_str = "_".join(f"{k}_{v}" for k, v in sorted(kwargs.items()))
    return f"{analysis_type}_{text_hash}_{kwargs_str}"

def safe_json_serialize(obj: Any) -> str:
    """Safely serialize objects to JSON"""
    try:
        return json.dumps(obj, default=str, indent=2)
    except (TypeError, ValueError) as e:
        logger.warning(f"JSON serialization failed: {e}")
        return json.dumps({"error": "Serialization failed", "type": str(type(obj))})