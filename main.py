"""
TraeGuard Main Module: Entry point for TRAE-powered Reliability & Responsible AI Lab

This module provides the main interface for TraeGuard functionality,
integrating Reliability Lab, RAI Studio, and Green Privacy modules.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import base classes and utilities
from .base import BaseAnalyzer, AnalysisResult, MetricsCollector, CacheManager
from .base import create_cache_key, safe_json_serialize

# Import configuration
try:
    import config
    TRAEGUARD_ENABLED = config.TRAEGUARD_ENABLED
except (ImportError, AttributeError):
    TRAEGUARD_ENABLED = False
    logging.warning("TraeGuard configuration not available. Some features may be limited.")

# Initialize logger
logger = logging.getLogger(__name__)

class TraeGuardOrchestrator:
    """
    Main orchestrator for TraeGuard analysis pipeline.
    
    Coordinates analysis across Reliability Lab, RAI Studio, and Green Privacy modules.
    """
    
    def __init__(self, enable_caching: bool = True):
        self.enable_caching = enable_caching
        self.metrics_collector = MetricsCollector()
        self.cache_manager = CacheManager(max_size=1000, ttl=3600) if enable_caching else None
        self.analyzers = {}
        
        # Initialize analyzers if TraeGuard is enabled
        if TRAEGUARD_ENABLED:
            self._initialize_analyzers()
        else:
            logger.warning("TraeGuard not fully enabled due to configuration issues")
    
    def _initialize_analyzers(self):
        """Initialize all TraeGuard analyzers"""
        try:
            # Import and initialize analyzers
            from .reliability import ReliabilityAnalyzer
            from .rai import RAIAnalyzer
            from .green import GreenAnalyzer
            
            self.analyzers = {
                'reliability': ReliabilityAnalyzer(),
                'rai': RAIAnalyzer(),
                'green': GreenAnalyzer()
            }
            logger.info("Successfully initialized TraeGuard analyzers")
            
        except Exception as e:
            logger.error(f"Failed to initialize analyzers: {e}")
            self.analyzers = {}
    
    def analyze_policy(self, policy_text: str, 
                      enable_reliability: bool = True,
                      enable_rai: bool = True,
                      enable_green: bool = True,
                      **kwargs) -> Dict[str, Any]:
        """
        Perform comprehensive TraeGuard analysis on a privacy policy.
        
        Args:
            policy_text: The privacy policy text to analyze
            enable_reliability: Whether to run reliability analysis
            enable_rai: Whether to run RAI analysis
            enable_green: Whether to run green privacy analysis
            **kwargs: Additional parameters for specific analyses
            
        Returns:
            Dictionary containing all analysis results
        """
        start_time = datetime.now()
        
        # Check cache first
        if self.cache_manager:
            cache_key = create_cache_key(policy_text, "traeguard_combined", 
                                       reliability=enable_reliability,
                                       rai=enable_rai, 
                                       green=enable_green)
            cached_result = self.cache_manager.get(cache_key)
            if cached_result:
                logger.info("Returning cached TraeGuard analysis result")
                return cached_result
        
        logger.info(f"Starting TraeGuard analysis (reliability={enable_reliability}, rai={enable_rai}, green={enable_green})")
        
        results = {
            "timestamp": start_time.isoformat(),
            "policy_length": len(policy_text),
            "traeguard_version": getattr(config, 'TRAEGUARD_VERSION', '1.0.0'),
            "analyses": {},
            "metadata": {
                "reliability_enabled": enable_reliability,
                "rai_enabled": enable_rai,
                "green_enabled": enable_green,
                "caching_enabled": self.enable_caching
            }
        }
        
        # Run enabled analyses
        if enable_reliability and 'reliability' in self.analyzers:
            try:
                reliability_result = self.analyzers['reliability'].analyze(policy_text, **kwargs)
                results["analyses"]["reliability"] = reliability_result.to_dict()
                self.metrics_collector.record_metric("reliability_analysis_time", 
                                                   (datetime.now() - start_time).total_seconds())
            except Exception as e:
                logger.error(f"Reliability analysis failed: {e}")
                results["analyses"]["reliability"] = {"error": str(e), "status": "failed"}
        
        if enable_rai and 'rai' in self.analyzers:
            try:
                rai_result = self.analyzers['rai'].analyze(policy_text, **kwargs)
                results["analyses"]["rai"] = rai_result.to_dict()
                self.metrics_collector.record_metric("rai_analysis_time", 
                                                   (datetime.now() - start_time).total_seconds())
            except Exception as e:
                logger.error(f"RAI analysis failed: {e}")
                results["analyses"]["rai"] = {"error": str(e), "status": "failed"}
        
        if enable_green and 'green' in self.analyzers:
            try:
                green_result = self.analyzers['green'].analyze(policy_text, **kwargs)
                results["analyses"]["green"] = green_result.to_dict()
                self.metrics_collector.record_metric("green_analysis_time", 
                                                   (datetime.now() - start_time).total_seconds())
            except Exception as e:
                logger.error(f"Green analysis failed: {e}")
                results["analyses"]["green"] = {"error": str(e), "status": "failed"}
        
        # Add overall metrics
        total_time = (datetime.now() - start_time).total_seconds()
        results["metadata"]["total_analysis_time"] = total_time
        results["metadata"]["completed_analyses"] = len([a for a in results["analyses"].values() if a.get("status") == "success"])
        
        # Cache the result
        if self.cache_manager:
            self.cache_manager.set(cache_key, results)
        
        logger.info(f"TraeGuard analysis completed in {total_time:.2f}s")
        return results
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get collected metrics"""
        return self.metrics_collector.export_metrics()
    
    def clear_cache(self):
        """Clear analysis cache"""
        if self.cache_manager:
            self.cache_manager.clear()
            logger.info("TraeGuard cache cleared")
    
    def get_status(self) -> Dict[str, Any]:
        """Get TraeGuard system status"""
        return {
            "enabled": TRAEGUARD_ENABLED,
            "version": getattr(config, 'TRAEGUARD_VERSION', '1.0.0'),
            "analyzers_loaded": list(self.analyzers.keys()),
            "caching_enabled": self.enable_caching,
            "cache_size": len(self.cache_manager.cache) if self.cache_manager else 0,
            "metrics_collected": len(self.metrics_collector.metrics)
        }

# Global orchestrator instance
traeguard_orchestrator = TraeGuardOrchestrator() if TRAEGUARD_ENABLED else None

def analyze_policy(policy_text: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function for policy analysis.
    
    Args:
        policy_text: The privacy policy text to analyze
        **kwargs: Additional parameters for analysis
        
    Returns:
        Dictionary containing all analysis results
    """
    if not traeguard_orchestrator:
        logger.error("TraeGuard orchestrator not available")
        return {"error": "TraeGuard not available", "status": "failed"}
    
    return traeguard_orchestrator.analyze_policy(policy_text, **kwargs)

def get_traeguard_status() -> Dict[str, Any]:
    """Get TraeGuard system status"""
    if not traeguard_orchestrator:
        return {"enabled": False, "error": "TraeGuard not available"}
    
    return traeguard_orchestrator.get_status()

# Export main classes and functions
__all__ = [
    "TraeGuardOrchestrator",
    "BaseAnalyzer", 
    "AnalysisResult",
    "MetricsCollector",
    "CacheManager",
    "analyze_policy",
    "get_traeguard_status",
    "traeguard_orchestrator"
]