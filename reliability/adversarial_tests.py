"""
Adversarial Testing Module for TraeGuard

This module implements adversarial and robustness testing for privacy policy clauses
by generating semantic variants and measuring classifier stability.
"""

import re
import random
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging

# Import existing PrivyReveal components
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core_logic import classify_sentences, get_explainer_pipeline
from models import id2label
from config import THRESHOLD

logger = logging.getLogger(__name__)


@dataclass
class ClauseVariant:
    """Represents a generated variant of an original clause."""
    text: str
    variant_type: str
    description: str


@dataclass
class ClassificationResult:
    """Results from classifying a clause variant."""
    text: str
    top1_label: str
    rating: str
    case_score: float
    confidence: float
    top3: str
    probability_distribution: np.ndarray


@dataclass
class RobustnessMetrics:
    """Robustness metrics comparing original vs variants."""
    risk_drift_score: float
    label_stability_score: float
    confidence_stability: float
    probability_similarity: float
    variant_results: List[Dict[str, Any]]


class AdversarialTester:
    """Generates adversarial variants and tests classifier robustness."""
    
    def __init__(self, seed: int = 42):
        """Initialize the adversarial tester."""
        self.seed = seed
        random.seed(seed)
        np.random.seed(seed)
        
        # Paraphrase templates
        self.paraphrase_templates = {
            'collect': ['gather', 'obtain', 'acquire', 'retrieve'],
            'use': ['utilize', 'employ', 'apply', 'leverage'],
            'share': ['disclose', 'provide', 'transmit', 'distribute'],
            'store': ['retain', 'keep', 'save', 'maintain'],
            'process': ['handle', 'manage', 'analyze', 'evaluate'],
            'protect': ['safeguard', 'secure', 'defend', 'shield']
        }
        
        # Ambiguity introducers
        self.ambiguity_words = {
            'specific': ['certain', 'particular', 'specific'],
            'exactly': ['approximately', 'roughly', 'about'],
            'immediately': ['promptly', 'soon', 'in a timely manner'],
            'always': ['usually', 'generally', 'typically'],
            'all': ['most', 'many', 'the majority of'],
            'required': ['recommended', 'suggested', 'advised']
        }
        
        # Negation words
        self.negation_words = {
            'will': 'will not',
            'may': 'may not',
            'can': 'cannot',
            'do': 'do not',
            'does': 'does not',
            'collect': 'do not collect',
            'use': 'do not use',
            'share': 'do not share',
            'store': 'do not store'
        }

    def generate_paraphrased_variant(self, clause: str) -> ClauseVariant:
        """Generate a paraphrased variant of the clause."""
        text = clause.lower()
        
        # Replace key privacy verbs with synonyms
        for key, synonyms in self.paraphrase_templates.items():
            if key in text:
                replacement = random.choice(synonyms)
                text = text.replace(key, replacement)
        
        # Some basic syntactic transformations
        text = re.sub(r'we (\w+)', r'our company \1s', text)
        text = re.sub(r'your (\w+)', r'the user\'s \1', text)
        
        # Capitalize first letter
        text = text.capitalize()
        
        return ClauseVariant(
            text=text,
            variant_type="paraphrased",
            description="Clause with privacy verbs replaced by synonyms and minor syntactic changes"
        )

    def generate_negation_variant(self, clause: str) -> ClauseVariant:
        """Generate a negation-flipped variant of the clause."""
        text = clause
        
        # Add negations to key verbs
        for positive, negative in self.negation_words.items():
            pattern = r'\b' + re.escape(positive) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                text = re.sub(pattern, negative, text, flags=re.IGNORECASE)
                break
        
        # Handle some special cases
        if 'will' in text.lower() and 'will not' not in text.lower():
            text = re.sub(r'\bwill\b', 'will not', text, flags=re.IGNORECASE)
        elif re.search(r'\bno\s+longer\b', text, re.IGNORECASE):
            text = re.sub(r'\bno\s+longer\b', '', text, flags=re.IGNORECASE)
        
        return ClauseVariant(
            text=text,
            variant_type="negation_flipped",
            description="Clause with negations added to key action verbs"
        )

    def generate_ambiguous_variant(self, clause: str) -> ClauseVariant:
        """Generate a more ambiguous variant of the clause."""
        text = clause
        
        # Replace specific terms with vague ones
        for specific, vague_options in self.ambiguity_words.items():
            if specific in text.lower():
                vague = random.choice(vague_options)
                text = re.sub(r'\b' + re.escape(specific) + r'\b', vague, text, flags=re.IGNORECASE)
        
        # Replace specific numbers/durations
        text = re.sub(r'\b\d+\s+days?\b', 'a reasonable period', text, flags=re.IGNORECASE)
        text = re.sub(r'\b\d+\s+weeks?\b', 'some time', text, flags=re.IGNORECASE)
        text = re.sub(r'\b\d+\s+months?\b', 'an extended period', text, flags=re.IGNORECASE)
        
        # Replace specific percentages
        text = re.sub(r'\b\d+%\b', 'a significant percentage', text)
        
        return ClauseVariant(
            text=text,
            variant_type="ambiguous",
            description="Clause with specific terms replaced by vague language"
        )

    def generate_entity_swapped_variant(self, clause: str) -> ClauseVariant:
        """Generate an entity-swapped variant of the clause."""
        text = clause
        
        # Company name swaps
        company_replacements = {
            'Google': ['Microsoft', 'Apple', 'Amazon', 'Meta'],
            'Facebook': ['Twitter', 'LinkedIn', 'Instagram', 'TikTok'],
            'Amazon': ['eBay', 'Walmart', 'Target', 'Best Buy'],
            'Apple': ['Samsung', 'Google', 'Microsoft', 'Sony'],
            'Microsoft': ['Google', 'Apple', 'IBM', 'Oracle']
        }
        
        for original, replacements in company_replacements.items():
            if original in text:
                replacement = random.choice(replacements)
                text = text.replace(original, replacement)
        
        # Generic entity swaps
        text = re.sub(r'\bCompany\b', 'Organization', text)
        text = re.sub(r'\bCorporation\b', 'Entity', text)
        text = re.sub(r'\bInc\b', 'LLC', text)
        
        # Date swaps (simplified)
        text = re.sub(r'\b2023\b', '2024', text)
        text = re.sub(r'\b2024\b', '2025', text)
        
        # Duration swaps
        duration_swaps = {
            '30 days': '60 days',
            '60 days': '90 days', 
            '90 days': '120 days',
            '1 year': '2 years',
            '2 years': '3 years'
        }
        
        for original, replacement in duration_swaps.items():
            if original in text:
                text = text.replace(original, replacement)
                break
        
        return ClauseVariant(
            text=text,
            variant_type="entity_swapped",
            description="Clause with company names, dates, and durations swapped"
        )

    def generate_variants(self, clause: str, num_variants: int = 4) -> List[ClauseVariant]:
        """Generate multiple variants of a clause."""
        variant_generators = [
            self.generate_paraphrased_variant,
            self.generate_negation_variant,
            self.generate_ambiguous_variant,
            self.generate_entity_swapped_variant
        ]
        
        variants = []
        for i in range(min(num_variants, len(variant_generators))):
            try:
                variant = variant_generators[i](clause)
                variants.append(variant)
            except Exception as e:
                logger.warning(f"Failed to generate variant {i} for clause: {e}")
                continue
        
        return variants

    def classify_clause(self, clause: str) -> ClassificationResult:
        """Classify a single clause using existing PrivyReveal classifier."""
        try:
            # Use existing classifier
            results_df = classify_sentences([clause])
            
            if results_df.empty:
                raise ValueError("Classification returned empty results")
            
            result = results_df.iloc[0]
            
            # Get probability distribution from explainer pipeline
            explainer = get_explainer_pipeline()
            prob_dist = explainer.predict_proba([clause])[0]
            
            return ClassificationResult(
                text=clause,
                top1_label=result['top1_label'],
                rating=result['rating'],
                case_score=result['case_score'],
                confidence=result['confidence'],
                top3=result['top3'],
                probability_distribution=prob_dist
            )
            
        except Exception as e:
            logger.error(f"Classification failed for clause '{clause}': {e}")
            raise

    def calculate_robustness_metrics(self, original: ClassificationResult, 
                                     variants: List[ClassificationResult]) -> RobustnessMetrics:
        """Calculate robustness metrics comparing original vs variants."""
        if not variants:
            return RobustnessMetrics(
                risk_drift_score=0.0,
                label_stability_score=1.0,
                confidence_stability=1.0,
                probability_similarity=1.0,
                variant_results=[]
            )
        
        variant_results = []
        risk_drifts = []
        label_stabilities = []
        confidence_stabilities = []
        probability_similarities = []
        
        for variant in variants:
            # Risk drift: normalized difference in case scores
            risk_drift = abs(variant.case_score - original.case_score) / max(abs(original.case_score), 1.0)
            risk_drifts.append(risk_drift)
            
            # Label stability: 1.0 if same label, decreases with probability shift
            if variant.top1_label == original.top1_label:
                label_stability = 1.0
            else:
                # Get index of original label in variant distribution
                try:
                    original_label_idx = list(id2label.values()).index(original.top1_label)
                    original_prob_in_variant = variant.probability_distribution[original_label_idx]
                    label_stability = original_prob_in_variant
                except (ValueError, IndexError):
                    label_stability = 0.0
            label_stabilities.append(label_stability)
            
            # Confidence stability: normalized difference in confidence
            confidence_stability = 1.0 - abs(variant.confidence - original.confidence)
            confidence_stabilities.append(confidence_stability)
            
            # Probability similarity: cosine similarity between distributions
            prob_sim = self._cosine_similarity(original.probability_distribution, 
                                              variant.probability_distribution)
            probability_similarities.append(prob_sim)
            
            variant_results.append({
                'text': variant.text,
                'variant_type': 'paraphrased' if 'paraphrased' in variant.text.lower() else 
                              'negation_flipped' if 'not' in variant.text.lower() else
                              'ambiguous' if any(word in variant.text.lower() for word in ['certain', 'approximately']) else
                              'entity_swapped',
                'top1_label': variant.top1_label,
                'rating': variant.rating,
                'case_score': variant.case_score,
                'confidence': variant.confidence,
                'risk_drift': risk_drift,
                'label_stability': label_stability,
                'confidence_stability': confidence_stability,
                'probability_similarity': prob_sim
            })
        
        # Aggregate metrics
        avg_risk_drift = np.mean(risk_drifts) if risk_drifts else 0.0
        avg_label_stability = np.mean(label_stabilities) if label_stabilities else 0.0
        avg_confidence_stability = np.mean(confidence_stabilities) if confidence_stabilities else 0.0
        avg_probability_similarity = np.mean(probability_similarities) if probability_similarities else 0.0
        
        # Normalize final scores (0-1 range)
        risk_drift_score = min(1.0, avg_risk_drift)
        label_stability_score = avg_label_stability
        
        return RobustnessMetrics(
            risk_drift_score=risk_drift_score,
            label_stability_score=label_stability_score,
            confidence_stability=avg_confidence_stability,
            probability_similarity=avg_probability_similarity,
            variant_results=variant_results
        )

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)

    def test_clause_robustness(self, clause: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Test robustness of a single clause against adversarial variants."""
        logger.info(f"Testing robustness for clause: {clause[:50]}...")
        
        # Classify original clause
        original_result = self.classify_clause(clause)
        
        # Generate variants
        variants = self.generate_variants(clause)
        
        # Classify each variant
        variant_results = []
        for variant in variants:
            try:
                variant_result = self.classify_clause(variant.text)
                variant_results.append(variant_result)
            except Exception as e:
                logger.warning(f"Failed to classify variant: {e}")
                continue
        
        # Calculate robustness metrics
        robustness_metrics = self.calculate_robustness_metrics(original_result, variant_results)
        
        return {
            'original': {
                'text': original_result.text,
                'top1_label': original_result.top1_label,
                'rating': original_result.rating,
                'case_score': original_result.case_score,
                'confidence': original_result.confidence,
                'top3': original_result.top3
            },
            'robustness_metrics': {
                'risk_drift_score': robustness_metrics.risk_drift_score,
                'label_stability_score': robustness_metrics.label_stability_score,
                'confidence_stability': robustness_metrics.confidence_stability,
                'probability_similarity': robustness_metrics.probability_similarity
            },
            'variants': robustness_metrics.variant_results,
            'metadata': metadata or {}
        }


def run_robustness_suite(clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run comprehensive robustness testing on a list of clauses.
    
    Args:
        clauses: List of dictionaries with 'text' and optional 'metadata'
    
    Returns:
        JSON-serializable summary of robustness testing results
    """
    logger.info(f"Running robustness suite on {len(clauses)} clauses")
    
    tester = AdversarialTester()
    results = []
    
    for i, clause_data in enumerate(clauses):
        clause_text = clause_data.get('text', '')
        metadata = clause_data.get('metadata', {})
        
        if not clause_text:
            logger.warning(f"Empty clause at index {i}, skipping")
            continue
        
        try:
            result = tester.test_clause_robustness(clause_text, metadata)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to test clause {i}: {e}")
            results.append({
                'original': {'text': clause_text, 'error': str(e)},
                'robustness_metrics': {},
                'variants': [],
                'metadata': metadata
            })
    
    # Calculate aggregate statistics
    if results:
        risk_drifts = [r['robustness_metrics'].get('risk_drift_score', 0) for r in results if 'robustness_metrics' in r]
        label_stabilities = [r['robustness_metrics'].get('label_stability_score', 0) for r in results if 'robustness_metrics' in r]
        
        avg_risk_drift = np.mean(risk_drifts) if risk_drifts else 0.0
        avg_label_stability = np.mean(label_stabilities) if label_stabilities else 0.0
        
        overall_robustness = 1.0 - avg_risk_drift
    else:
        avg_risk_drift = 0.0
        avg_label_stability = 0.0
        overall_robustness = 0.0
    
    return {
        'summary': {
            'total_clauses': len(clauses),
            'successful_tests': len([r for r in results if 'error' not in r.get('original', {})]),
            'average_risk_drift': avg_risk_drift,
            'average_label_stability': avg_label_stability,
            'overall_robustness_score': overall_robustness
        },
        'detailed_results': results,
        'timestamp': np.datetime64('now').astype(str)
    }


if __name__ == "__main__":
    # Example usage
    test_clauses = [
        {
            "text": "We collect your personal information to provide our services.",
            "metadata": {"clause_id": "test_1", "policy_section": "data_collection"}
        },
        {
            "text": "We may share your data with third-party partners for marketing purposes.",
            "metadata": {"clause_id": "test_2", "policy_section": "data_sharing"}
        }
    ]
    
    results = run_robustness_suite(test_clauses)
    print(f"Robustness testing completed. Overall robustness score: {results['summary']['overall_robustness_score']:.3f}")
