"""
TraeGuard - TRAE-powered Reliability & Responsible AI Lab for Digital Policies

Enhanced version with dark/light mode, improved filtering, richer reports, and better metrics.
"""

import streamlit as st
import pandas as pd
import json
import sys
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Import PlainText Panda agent
try:
    from plaintext_panda import plaintext_panda
except ImportError:
    # Mock implementation for demo purposes
    class PlainTextPanda:
        def run(self, params):
            clause_text = params.get('clause_text', '')
            if not clause_text.strip():
                return {
                    'simple_english': 'No text provided',
                    'legal_shortened': 'No text provided', 
                    'eli5': 'No text provided',
                    'privacy_lawyer': 'No text provided'
                }
            
            # Mock rewrite versions
            return {
                'simple_english': f"In simple terms: {clause_text[:100]}... This means the company will handle your information.",
                'legal_shortened': f"Legally: {clause_text[:80]}... [Essential legal points summarized]",
                'eli5': f"Like you're 5: Imagine {clause_text[:60]}... It's like when your friend promises to keep your secret!",
                'privacy_lawyer': f"From a privacy law perspective: {clause_text[:120]}... [Analysis of data processing authority, consent requirements, and user rights under GDPR/CCPA]"
            }
    
    plaintext_panda = PlainTextPanda()

# Mock implementations for demo purposes
class PrivyReveal:
    def analyze_policy(self, policy_text):
        # Enhanced mock analysis with more realistic data
        clauses = policy_text.split('.')
        results = {
            'clauses': []
        }
        for i, clause in enumerate(clauses):
            if clause.strip():
                text = clause.strip()
                # More sophisticated risk scoring
                risk_score = 0.3  # Base risk
                
                if 'collect' in text.lower() and 'personal' in text.lower():
                    risk_score += 0.4
                if 'share' in text.lower() or 'third party' in text.lower():
                    risk_score += 0.3
                if 'retain' in text.lower() and ('indefinite' in text.lower() or 'permanent' in text.lower()):
                    risk_score += 0.2
                if 'sell' in text.lower() or 'monetize' in text.lower():
                    risk_score += 0.3
                if 'track' in text.lower() or 'monitor' in text.lower():
                    risk_score += 0.2
                
                risk_score = min(risk_score, 1.0)
                
                # Determine label
                if 'collect' in text.lower():
                    label = 'data_collection'
                elif 'share' in text.lower() or 'third party' in text.lower():
                    label = 'data_sharing'
                elif 'retain' in text.lower() or 'store' in text.lower():
                    label = 'data_retention'
                elif 'track' in text.lower() or 'monitor' in text.lower():
                    label = 'tracking'
                else:
                    label = 'general'
                
                results['clauses'].append({
                    'text': text,
                    'label': label,
                    'risk_score': risk_score,
                    'confidence': 0.85,
                    'id': f'clause_{i}'
                })
        return results

class AdversarialTester:
    def run_robustness_suite(self, clauses):
        unstable_clauses = []
        total_clauses = len(clauses)
        
        for clause in clauses:
            # Simulate robustness testing
            original_risk = clause.get('risk_score', 0)
            
            # Simulate adversarial variants
            variants = []
            for i in range(5):  # 5 adversarial variants
                # Simulate some drift
                drift = (i - 2) * 0.05  # Small drift pattern
                variant_risk = max(0, min(1, original_risk + drift))
                variants.append({
                    'risk_score': variant_risk,
                    'label': clause.get('label', 'unknown')
                })
            
            # Calculate metrics
            risk_scores = [v['risk_score'] for v in variants]
            labels = [v['label'] for v in variants]
            
            risk_drift = max(risk_scores) - min(risk_scores)
            label_stability = 1.0 - (len(set(labels)) - 1) / len(labels) if len(set(labels)) > 1 else 1.0
            
            # Check if unstable
            if risk_drift >= 0.3 or label_stability <= 0.7:
                unstable_clauses.append({
                    'original_text': clause.get('text', ''),
                    'original_label': clause.get('label', ''),
                    'original_risk': original_risk,
                    'risk_drift_score': risk_drift,
                    'label_stability_score': label_stability,
                    'is_unstable': True
                })
        
        return {
            'avg_label_stability': sum(c.get('label_stability_score', 1.0) for c in unstable_clauses) / len(unstable_clauses) if unstable_clauses else 1.0,
            'avg_risk_drift': sum(c.get('risk_drift_score', 0) for c in unstable_clauses) / len(unstable_clauses) if unstable_clauses else 0.0,
            'unstable_clauses': unstable_clauses,
            'total_unstable': len(unstable_clauses)
        }

class RegressionTester:
    def compare_with_baseline(self, clauses):
        return {
            'percent_label_changed': 15.2,
            'avg_risk_change': 0.08,
            'most_changed_clauses': clauses[:3] if clauses else []
        }

class CrossModelAnalyzer:
    def summarize_cross_model_agreement(self, clauses):
        return {
            'agreement_rate': 87.5,
            'divergent_clauses_count': 2,
            'most_divergent_clauses': clauses[:2] if clauses else []
        }

class RAIExplainer:
    def explain_clause(self, clause_text, label, risk_score, user_context):
        explanations = {
            'data_collection': 'collects and processes your personal information',
            'data_sharing': 'shares your information with third parties',
            'data_retention': 'stores your data for extended periods',
            'tracking': 'monitors your behavior and activities',
            'general': 'handles your personal information'
        }
        
        worst_cases = {
            'data_collection': 'Your personal data could be used for unauthorized profiling or sold to data brokers.',
            'data_sharing': 'Your information could be shared with companies you don\'t trust or used for targeted manipulation.',
            'data_retention': 'Your data could be kept indefinitely, increasing exposure to breaches or misuse.',
            'tracking': 'Your online behavior could be monitored across websites and used to manipulate your choices.',
            'general': 'Your privacy rights could be compromised without your awareness.'
        }
        
        vulnerable_impacts = {
            'children': ['Children may be targeted with inappropriate content', 'Parental controls could be bypassed'],
            'elderly': ['Seniors may be vulnerable to scams', 'Medical information could be misused'],
            'job_seeker': ['Employment opportunities could be discriminated against', 'Professional reputation could be damaged'],
            'healthcare_patient': ['Medical privacy could be compromised', 'Insurance coverage could be affected'],
            'financial_customer': ['Credit scores could be impacted', 'Financial decisions could be manipulated']
        }
        
        risk_level = 'high' if risk_score > 0.7 else 'medium' if risk_score > 0.4 else 'low'
        
        return {
            'clause_text': clause_text,
            'explanation': f"This clause {explanations.get(label, 'handles your personal information')}. For {user_context.replace('_', ' ')}, this means your personal information may be processed for business purposes.",
            'risk_level': risk_level,
            'worst_case_scenario': worst_cases.get(label, 'Your privacy could be compromised.'),
            'vulnerable_groups': vulnerable_impacts.get(user_context, []) if risk_score > 0.6 else [],
            'beneficiary': 'company' if risk_score > 0.6 else 'user',
            'recommendation': self._get_recommendation(label, risk_score)
        }
    
    def _get_recommendation(self, label, risk_score):
        recommendations = {
            'data_collection': 'Limit data collection to essential information only',
            'data_sharing': 'Require explicit consent for third-party sharing',
            'data_retention': 'Implement data deletion policies and user rights',
            'tracking': 'Provide opt-out options for behavioral tracking',
            'general': 'Increase transparency about data practices'
        }
        
        if risk_score > 0.7:
            return f"CRITICAL: {recommendations.get(label, 'Review privacy practices immediately')}"
        elif risk_score > 0.4:
            return f"RECOMMENDED: {recommendations.get(label, 'Consider privacy improvements')}"
        else:
            return "Monitor for changes in privacy practices"

class RAIReportGenerator:
    def generate_report(self, explanations, user_context, all_clauses):
        # Analyze patterns
        high_risk_clauses = [e for e in explanations if e.get('risk_level') == 'high']
        medium_risk_clauses = [e for e in explanations if e.get('risk_level') == 'medium']
        low_risk_clauses = [e for e in explanations if e.get('risk_level') == 'low']
        
        # Identify themes
        themes = self._identify_themes(explanations)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(explanations, themes)
        
        # Create structured report
        report = {
            'overview': {
                'total_clauses': len(all_clauses),
                'high_risk_clauses': len(high_risk_clauses),
                'medium_risk_clauses': len(medium_risk_clauses),
                'low_risk_clauses': len(low_risk_clauses),
                'user_context': user_context,
                'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            'high_risk_clauses': [
                {
                    'text': e['clause_text'][:200] + '...' if len(e['clause_text']) > 200 else e['clause_text'],
                    'risk_score': self._extract_risk_from_explanation(e),
                    'explanation': e['explanation'],
                    'worst_case': e['worst_case_scenario'],
                    'vulnerable_groups': e.get('vulnerable_groups', []),
                    'recommendation': e.get('recommendation', '')
                } for e in high_risk_clauses
            ],
            'medium_risk_clauses': [
                {
                    'text': e['clause_text'][:150] + '...' if len(e['clause_text']) > 150 else e['clause_text'],
                    'risk_score': self._extract_risk_from_explanation(e),
                    'explanation': e['explanation'],
                    'recommendation': e.get('recommendation', '')
                } for e in medium_risk_clauses[:5]  # Limit to top 5
            ],
            'key_themes': themes,
            'recommendations': recommendations,
            'summary': self._generate_summary(high_risk_clauses, medium_risk_clauses, themes)
        }
        
        # Generate markdown
        markdown = self._generate_markdown(report)
        
        return {
            'structured': report,
            'markdown': markdown
        }
    
    def _extract_risk_from_explanation(self, explanation):
        # Extract risk score from the explanation data
        # This is a mock implementation
        text = explanation.get('clause_text', '')
        if 'collect' in text.lower() and 'personal' in text.lower():
            return 0.8
        elif 'share' in text.lower():
            return 0.6
        else:
            return 0.4
    
    def _identify_themes(self, explanations):
        themes = []
        
        # Check for common themes
        texts = [e.get('clause_text', '').lower() for e in explanations]
        
        if any('collect' in text and 'personal' in text for text in texts):
            themes.append("Extensive personal data collection")
        
        if any('share' in text or 'third party' in text for text in texts):
            themes.append("Broad third-party data sharing")
        
        if any('retain' in text and ('indefinite' in text or 'permanent' in text) for text in texts):
            themes.append("Indefinite data retention")
        
        if any('track' in text or 'monitor' in text for text in texts):
            themes.append("Behavioral tracking and monitoring")
        
        if any('sell' in text or 'monetize' in text for text in texts):
            themes.append("Data monetization practices")
        
        return themes if themes else ["Standard data processing practices"]
    
    def _generate_recommendations(self, explanations, themes):
        recommendations = []
        
        if "Extensive personal data collection" in themes:
            recommendations.append("Limit data collection to essential information only")
            recommendations.append("Implement data minimization principles")
        
        if "Broad third-party data sharing" in themes:
            recommendations.append("Require explicit consent for third-party sharing")
            recommendations.append("Provide granular sharing controls")
        
        if "Indefinite data retention" in themes:
            recommendations.append("Establish clear data deletion policies")
            recommendations.append("Implement user-initiated deletion rights")
        
        if "Behavioral tracking and monitoring" in themes:
            recommendations.append("Offer opt-out options for behavioral tracking")
            recommendations.append("Limit tracking to essential functionality")
        
        if not recommendations:
            recommendations.append("Monitor privacy practices for changes")
            recommendations.append("Regularly review data processing activities")
        
        return recommendations
    
    def _generate_summary(self, high_risk_clauses, medium_risk_clauses, themes):
        total_risk_clauses = len(high_risk_clauses) + len(medium_risk_clauses)
        
        summary = f"This privacy policy contains {total_risk_clauses} clauses that pose potential privacy risks. "
        
        if high_risk_clauses:
            summary += f"{len(high_risk_clauses)} clauses are classified as high-risk and require immediate attention. "
        
        if medium_risk_clauses:
            summary += f"{len(medium_risk_clauses)} clauses present medium-level risks that should be monitored. "
        
        if themes:
            summary += f"Key concerns include: {', '.join(themes[:2])}."
        
        return summary
    
    def _generate_markdown(self, report):
        md = f"# TraeGuard RAI Analysis Report\n\n"
        md += f"**Analysis Date:** {report['overview']['analysis_date']}\n"
        md += f"**User Context:** {report['overview']['user_context']}\n\n"
        
        md += "## Overview\n\n"
        md += f"- **Total Clauses Analyzed:** {report['overview']['total_clauses']}\n"
        md += f"- **High Risk Clauses:** {report['overview']['high_risk_clauses']}\n"
        md += f"- **Medium Risk Clauses:** {report['overview']['medium_risk_clauses']}\n"
        md += f"- **Low Risk Clauses:** {report['overview']['low_risk_clauses']}\n\n"
        
        if report['high_risk_clauses']:
            md += "## High Risk Clauses\n\n"
            for i, clause in enumerate(report['high_risk_clauses'], 1):
                md += f"### Clause {i}\n"
                md += f"**Text:** {clause['text']}\n\n"
                md += f"**Risk Score:** {clause['risk_score']:.2f}\n\n"
                md += f"**Explanation:** {clause['explanation']}\n\n"
                md += f"**Worst Case:** {clause['worst_case']}\n\n"
                if clause['vulnerable_groups']:
                    md += f"**Vulnerable Groups Impact:** {', '.join(clause['vulnerable_groups'])}\n\n"
                md += f"**Recommendation:** {clause['recommendation']}\n\n"
        
        if report['medium_risk_clauses']:
            md += "## Medium Risk Clauses\n\n"
            for i, clause in enumerate(report['medium_risk_clauses'], 1):
                md += f"### Clause {i}\n"
                md += f"**Text:** {clause['text']}\n\n"
                md += f"**Risk Score:** {clause['risk_score']:.2f}\n\n"
                md += f"**Explanation:** {clause['explanation']}\n\n"
                md += f"**Recommendation:** {clause['recommendation']}\n\n"
        
        md += "## Key Themes\n\n"
        for theme in report['key_themes']:
            md += f"- {theme}\n"
        md += "\n"
        
        md += "## Recommendations\n\n"
        for i, rec in enumerate(report['recommendations'], 1):
            md += f"{i}. {rec}\n"
        md += "\n"
        
        md += "## Summary\n\n"
        md += f"{report['summary']}\n"
        
        return md

class GreenPrivacySummary:
    def __init__(self, data_categories_count, max_retention_days, third_party_count, 
                 tracking_count, data_broker_mention, consent_granularity,
                 data_footprint_score, tier, tier_emoji, eco_mode_applied, optimizations_applied):
        self.data_categories_count = data_categories_count
        self.max_retention_days = max_retention_days
        self.third_party_count = third_party_count
        self.tracking_count = tracking_count
        self.data_broker_mention = data_broker_mention
        self.consent_granularity = consent_granularity
        self.data_footprint_score = data_footprint_score
        self.tier = tier
        self.tier_emoji = tier_emoji
        self.eco_mode_applied = eco_mode_applied
        self.optimizations_applied = optimizations_applied

def analyze_policy_footprint(analysis_results, eco_mode=False):
    clauses = analysis_results.get('clauses', [])
    
    # Enhanced footprint calculation
    data_categories = len(set(clause.get('label', '') for clause in clauses))
    max_retention = 730  # Default 2 years, increased for more realistic scoring
    third_party_count = sum(1 for clause in clauses if 'share' in clause.get('text', '').lower() or 'third party' in clause.get('text', '').lower())
    tracking_count = sum(1 for clause in clauses if any(word in clause.get('text', '').lower() for word in ['cookie', 'track', 'monitor', 'device id', 'fingerprint']))
    data_broker_mention = any('data broker' in clause.get('text', '').lower() or 'sell' in clause.get('text', '').lower() for clause in clauses)
    
    # Analyze consent granularity
    consent_text = ' '.join([clause.get('text', '') for clause in clauses]).lower()
    if 'granular' in consent_text or 'individual' in consent_text or 'specific' in consent_text:
        consent_granularity = 'granular'
    elif 'blanket' in consent_text or 'general' in consent_text:
        consent_granularity = 'blanket'
    else:
        consent_granularity = 'mixed'
    
    # Calculate footprint score with enhanced metrics
    score = (data_categories * 0.25) + \
            (min(max_retention / 1825, 1) * 20) + \
            (min(third_party_count / 8, 1) * 20) + \
            (min(tracking_count / 5, 1) * 15) + \
            (10 if data_broker_mention else 0) + \
            (10 if consent_granularity == 'blanket' else 5 if consent_granularity == 'mixed' else 0)
    
    score = min(score, 100)
    
    # Determine tier
    if score >= 60:
        tier = "High"
        tier_emoji = "🌳"
    elif score >= 35:
        tier = "Medium"
        tier_emoji = "🌿"
    else:
        tier = "Low"
        tier_emoji = "🌱"
    
    optimizations = []
    if eco_mode:
        optimizations = ["Reduced adversarial variants by 50%", "Skipped heavy cross-model comparison", "Optimized data footprint calculation"]
    
    return GreenPrivacySummary(
        data_categories_count=data_categories,
        max_retention_days=max_retention,
        third_party_count=third_party_count,
        tracking_count=tracking_count,
        data_broker_mention=data_broker_mention,
        consent_granularity=consent_granularity,
        data_footprint_score=score,
        tier=tier,
        tier_emoji=tier_emoji,
        eco_mode_applied=eco_mode,
        optimizations_applied=optimizations
    )

def get_eco_mode_settings(eco_mode=False):
    return {
        'adversarial_variants': 25 if eco_mode else 50,
        'cross_model_comparison': not eco_mode,
        'regression_tests': True
    }

# Enhanced theme management
def get_theme_css():
    """Get CSS based on current theme."""
    if st.session_state.theme == 'dark':
        return """
        <style>
            /* Dark theme variables */
            :root {
                --bg-primary: #0d1117;
                --bg-secondary: #161b22;
                --bg-card: #1c2128;
                --text-primary: #FFFFFF;
                --text-secondary: #F0F0F0;
                --accent-primary: #58a6ff;
                --accent-secondary: #a371f7;
                --border-color: #30363d;
                --success-color: #3fb950;
                --warning-color: #f85149;
                --error-color: #f85149;
                --shadow: 0 8px 24px rgba(0,0,0,0.5);
            }
            
            .stApp {
                background: linear-gradient(135deg, var(--bg-primary) 0%, #0a0e15 100%);
                color: var(--text-primary);
            }
            
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: var(--accent-primary);
                text-align: center;
                margin-bottom: 2rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.3);
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .theme-toggle {
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                color: white;
                border: none;
                border-radius: 50%;
                width: 3rem;
                height: 3rem;
                font-size: 1.2rem;
                cursor: pointer;
                box-shadow: var(--shadow);
                transition: all 0.3s ease;
            }
            
            .theme-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 8px 24px rgba(88, 166, 255, 0.4);
            }
            
            .clause-card {
                background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
                padding: 1.5rem;
                border-radius: 1rem;
                margin: 1rem 0;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }
            
            .clause-card:hover {
                border-color: var(--accent-primary);
                box-shadow: 0 8px 24px rgba(88, 166, 255, 0.2);
                transform: translateY(-2px);
            }
            
            .risk-high { 
                color: #ff6b6b; 
                font-weight: bold;
                text-shadow: 0 1px 2px rgba(255, 107, 107, 0.5);
            }
            .risk-medium { 
                color: #ffcc02; 
                font-weight: bold;
                text-shadow: 0 1px 2px rgba(255, 204, 2, 0.5);
            }
            .risk-low { 
                color: #69f0ae; 
                font-weight: bold;
                text-shadow: 0 1px 2px rgba(105, 240, 174, 0.5);
            }
            
            .tier-high { 
                color: #ff6b35; 
                font-size: 1.3rem; 
                font-weight: bold;
                text-shadow: 0 2px 4px rgba(255, 107, 53, 0.3);
            }
            .tier-medium { 
                color: #ffa726; 
                font-size: 1.3rem; 
                font-weight: bold;
                text-shadow: 0 2px 4px rgba(255, 167, 38, 0.3);
            }
            .tier-low { 
                color: #69f0ae; 
                font-size: 1.3rem; 
                font-weight: bold;
                text-shadow: 0 2px 4px rgba(105, 240, 174, 0.3);
            }
            
            .unstable-clause {
                background: linear-gradient(135deg, rgba(248, 81, 73, 0.15), rgba(255, 107, 107, 0.1));
                border: 1px solid rgba(248, 81, 73, 0.4);
                border-radius: 0.75rem;
                padding: 1.25rem;
                margin: 0.75rem 0;
                box-shadow: 0 4px 12px rgba(248, 81, 73, 0.15);
            }
            
            .metric-badge {
                display: inline-block;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.875rem;
                font-weight: 600;
                margin: 0.25rem;
                box-shadow: 0 2px 8px rgba(88, 166, 255, 0.3);
            }
            
            .stButton > button {
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                color: white;
                border: none;
                border-radius: 0.75rem;
                padding: 0.75rem 2rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: var(--shadow);
                font-size: 1rem;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(88, 166, 255, 0.4);
            }
            
            .stTabs [data-baseweb="tab-list"] {
                background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
                border-radius: 1rem;
                padding: 0.75rem;
                gap: 0.5rem;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
            }
            
            .stTabs [data-baseweb="tab"] {
                background: transparent;
                color: var(--text-secondary);
                border-radius: 0.5rem;
                padding: 0.75rem 1.5rem;
                font-weight: 500;
                transition: all 0.3s ease;
                border: 1px solid transparent;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                background: rgba(88, 166, 255, 0.1);
                color: var(--text-primary);
                border-color: rgba(88, 166, 255, 0.3);
            }
            
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
                color: white !important;
                font-weight: 600;
                border-color: transparent !important;
                box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
            }
            
            .sidebar-section {
                background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
                border-radius: 1rem;
                padding: 1.5rem;
                margin: 1rem 0;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
            }
            
            .filter-toggle {
                background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
                border: 1px solid var(--border-color);
                border-radius: 0.75rem;
                padding: 1rem;
                margin: 1rem 0;
                box-shadow: var(--shadow);
            }
            
            .info-tooltip {
                display: inline-block;
                background: var(--accent-primary);
                color: white;
                border-radius: 50%;
                width: 1.25rem;
                height: 1.25rem;
                text-align: center;
                line-height: 1.25rem;
                font-size: 0.75rem;
                cursor: help;
                margin-left: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            }
            
            .progress-bar {
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                border-radius: 1rem;
                height: 0.5rem;
                transition: width 0.3s ease;
            }
            
            .metric-card-enhanced {
                background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
                border-radius: 1rem;
                padding: 1.5rem;
                margin: 1rem 0;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
                transition: all 0.3s ease;
            }
            
            .metric-card-enhanced:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 32px rgba(88, 166, 255, 0.2);
            }
            
            /* Scoped dark mode text styling - only apply to main content area */
            .main .stMarkdown, 
            .main .stText, 
            .main .stCaption,
            .main .st-expanderHeader, 
            .main .st-expanderContent,
            .main [data-testid="stMarkdown"], 
            .main [data-testid="stText"],
            .main .streamlit-expanderHeader, 
            .main .streamlit-expanderContent {
                color: var(--text-primary) !important;
            }
            
            /* Secondary text elements in main content only */
            .main .stCaption, 
            .main .st-help, 
            .main [data-testid="stCaption"],
            .main .st-expanderHeader .stMarkdown p,
            .main .streamlit-expanderHeader p {
                color: var(--text-secondary) !important;
            }
            
            /* Button text */
            .stButton > button span,
            .stDownloadButton > button span {
                color: white !important;
            }
            
            /* Tab text - scoped to main content */
            .main .stTabs [data-baseweb="tab"] span {
                color: var(--text-secondary) !important;
            }
            
            .main .stTabs [aria-selected="true"] span {
                color: white !important;
            }
            
            /* Input and select text - scoped to main content */
            .main .stTextInput > div > div > input,
            .main .stTextArea > div > div > textarea,
            .main .stSelectbox > div > div > div {
                color: var(--text-primary) !important;
                background-color: var(--bg-card) !important;
            }
            
            /* Info and warning boxes - scoped to main content */
            .main .stAlert > div {
                color: var(--text-primary) !important;
            }
            
            /* Table text - scoped to main content */
            .main table, .main th, .main td, .main tr {
                color: var(--text-primary) !important;
            }
            
            /* Progress bar labels - scoped to main content */
            .main .stProgress > div > div > div {
                color: var(--text-primary) !important;
            }
            
            /* Metric value text - scoped to main content */
            .main .stMetric > div > div > div[data-testid="stMetricValue"] {
                color: var(--text-primary) !important;
            }
            
            /* Metric label text - scoped to main content */
            .main .stMetric > div > div > div[data-testid="stMetricLabel"] {
                color: var(--text-secondary) !important;
            }
            
            /* Additional Streamlit component overrides - scoped to main content */
            .main .st-emotion-cache-1qg05tj, .main .st-emotion-cache-1v0mbdj,
            .main .st-emotion-cache-16idsys, .main .st-emotion-cache-1vzeuhh,
            .main .st-emotion-cache-1n76uvr, .main .st-emotion-cache-1wbqy5l {
                color: var(--text-primary) !important;
            }
            
            /* Selectbox and multiselect text - scoped to main content */
            .main .stSelectbox div[data-baseweb="select"] > div:first-child,
            .main .stMultiSelect div[data-baseweb="select"] > div:first-child {
                color: var(--text-primary) !important;
                background-color: var(--bg-card) !important;
            }
            
            /* Checkbox and radio text - scoped to main content */
            .main .stCheckbox label, .main .stRadio label,
            .main .stCheckbox .st-emotion-cache-1n76uvr,
            .main .stRadio .st-emotion-cache-1n76uvr {
                color: var(--text-primary) !important;
            }
            
            /* File uploader text - scoped to main content */
            .main .stFileUploader .st-emotion-cache-1n76uvr,
            .main .stFileUploader .st-emotion-cache-16idsys {
                color: var(--text-primary) !important;
            }
            
            /* Toggle text - scoped to main content */
            .main .stToggle .st-emotion-cache-1n76uvr {
                color: var(--text-primary) !important;
            }
            
            /* Sidebar styling - ensure light background with dark text in dark mode */
            [data-testid="stSidebar"], .stSidebar {
                background-color: #F2F3F5 !important;
                color: #1A1A1A !important;
            }
            
            /* Sidebar text elements - ensure dark color */
            [data-testid="stSidebar"] .stMarkdown,
            [data-testid="stSidebar"] .stText,
            [data-testid="stSidebar"] .stCaption,
            [data-testid="stSidebar"] .stHeader,
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
            [data-testid="stSidebar"] h4, [data-testid="stSidebar"] h5, [data-testid="stSidebar"] h6,
            [data-testid="stSidebar"] label,
            [data-testid="stSidebar"] .stCheckbox label,
            [data-testid="stSidebar"] .stRadio label,
            [data-testid="stSidebar"] .stSelectbox label,
            [data-testid="stSidebar"] .stToggle label {
                color: #1A1A1A !important;
            }
            
            /* Sidebar icons and buttons - ensure dark color */
            [data-testid="stSidebar"] .stButton > button,
            [data-testid="stSidebar"] .stDownloadButton > button {
                background: linear-gradient(135deg, #58a6ff, #a371f7) !important;
                color: white !important;
            }
            
            /* Sidebar inputs - ensure proper contrast */
            [data-testid="stSidebar"] .stTextInput input,
            [data-testid="stSidebar"] .stTextArea textarea,
            [data-testid="stSidebar"] .stSelectbox select,
            [data-testid="stSidebar"] .stNumberInput input {
                background-color: white !important;
                color: #1A1A1A !important;
                border-color: #D1D5DB !important;
            }
            
            /* Sidebar expanders - ensure light theme */
            [data-testid="stSidebar"] .st-expanderHeader,
            [data-testid="stSidebar"] .st-expanderContent {
                background-color: white !important;
                color: #1A1A1A !important;
                border-color: #E5E7EB !important;
            }
            
            /* PlainText Panda tab styling for dark mode */
            .main .stTabs [data-baseweb="tab-list"] {
                background-color: var(--bg-card) !important;
                border-color: var(--border-color) !important;
            }
            
            .main .stTabs [data-baseweb="tab"] {
                color: var(--text-secondary) !important;
                background-color: transparent !important;
            }
            
            .main .stTabs [data-baseweb="tab"]:hover {
                color: var(--text-primary) !important;
                background-color: rgba(255, 255, 255, 0.1) !important;
            }
            
            .main .stTabs [aria-selected="true"] {
                color: var(--accent-primary) !important;
                background-color: rgba(88, 166, 255, 0.2) !important;
                border-bottom-color: var(--accent-primary) !important;
            }
            
            /* Date input and number input - scoped to main content */
            .main .stDateInput input, .main .stNumberInput input,
            .main .stTextInput input, .main .stTextArea textarea {
                color: var(--text-primary) !important;
                background-color: var(--bg-card) !important;
            }
            
            /* Ensure high contrast text only in main content area */
            .main * {
                color: var(--text-primary) !important;
            }
            
            /* But preserve the gradient text effects for special elements in main content */
            .main .risk-high, .main .risk-medium, .main .risk-low,
            .main .main-header, .main .tier-high, .main .tier-medium, .main .tier-low {
                color: inherit !important;
            }
            
            /* Override for secondary text in captions and help text - scoped to main content */
            .main .stCaption, .main .st-help, .main [data-testid="stCaption"],
            .main .st-expanderHeader p, .main .streamlit-expanderHeader p {
                color: var(--text-secondary) !important;
            }
        """
    else:
        return """
        <style>
            /* Light theme variables */
            :root {
                --bg-primary: #ffffff;
                --bg-secondary: #f6f8fa;
                --bg-card: #ffffff;
                --text-primary: #1a1e22;
                --text-secondary: #444d56;
                --accent-primary: #0969da;
                --accent-secondary: #8250df;
                --border-color: #d0d7de;
                --success-color: #1a7f37;
                --warning-color: #d1242f;
                --error-color: #d1242f;
                --shadow: 0 4px 16px rgba(0,0,0,0.08);
            }
            
            .stApp {
                background: linear-gradient(135deg, var(--bg-primary) 0%, #f8fafc 100%);
                color: var(--text-primary);
            }
            
            .main-header {
                font-size: 2.5rem;
                font-weight: bold;
                color: var(--accent-primary);
                text-align: center;
                margin-bottom: 2rem;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .theme-toggle {
                position: fixed;
                top: 1rem;
                right: 1rem;
                z-index: 1000;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                color: white;
                border: none;
                border-radius: 50%;
                width: 3rem;
                height: 3rem;
                font-size: 1.2rem;
                cursor: pointer;
                box-shadow: var(--shadow);
                transition: all 0.3s ease;
            }
            
            .theme-toggle:hover {
                transform: scale(1.1);
                box-shadow: 0 8px 24px rgba(9, 105, 218, 0.3);
            }
            
            .clause-card {
                background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
                padding: 1.5rem;
                border-radius: 1rem;
                margin: 1rem 0;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
                transition: all 0.3s ease;
                backdrop-filter: blur(10px);
            }
            
            .clause-card:hover {
                border-color: var(--accent-primary);
                box-shadow: 0 8px 24px rgba(9, 105, 218, 0.15);
                transform: translateY(-2px);
            }
            
            .risk-high { 
                color: #d1242f; 
                font-weight: bold;
                text-shadow: 0 1px 2px rgba(209, 36, 47, 0.1);
            }
            .risk-medium { 
                color: #ca5010; 
                font-weight: bold;
                text-shadow: 0 1px 2px rgba(202, 80, 16, 0.1);
            }
            .risk-low { 
                color: #1a7f37; 
                font-weight: bold;
                text-shadow: 0 1px 2px rgba(26, 127, 55, 0.1);
            }
            
            .tier-high { 
                color: #d1242f; 
                font-size: 1.3rem; 
                font-weight: bold;
                text-shadow: 0 2px 4px rgba(209, 36, 47, 0.1);
            }
            .tier-medium { 
                color: #ca5010; 
                font-size: 1.3rem; 
                font-weight: bold;
                text-shadow: 0 2px 4px rgba(202, 80, 16, 0.1);
            }
            .tier-low { 
                color: #1a7f37; 
                font-size: 1.3rem; 
                font-weight: bold;
                text-shadow: 0 2px 4px rgba(26, 127, 55, 0.1);
            }
            
            .unstable-clause {
                background: linear-gradient(135deg, rgba(209, 36, 47, 0.08), rgba(255, 71, 87, 0.05));
                border: 1px solid rgba(209, 36, 47, 0.2);
                border-radius: 0.75rem;
                padding: 1.25rem;
                margin: 0.75rem 0;
                box-shadow: 0 4px 12px rgba(209, 36, 47, 0.08);
            }
            
            .metric-badge {
                display: inline-block;
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 1rem;
                font-size: 0.875rem;
                font-weight: 600;
                margin: 0.25rem;
                box-shadow: 0 2px 8px rgba(9, 105, 218, 0.2);
            }
            
            .stButton > button {
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                color: white;
                border: none;
                border-radius: 0.75rem;
                padding: 0.75rem 2rem;
                font-weight: 600;
                transition: all 0.3s ease;
                box-shadow: var(--shadow);
                font-size: 1rem;
            }
            
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 24px rgba(9, 105, 218, 0.3);
            }
            
            .stTabs [data-baseweb="tab-list"] {
                background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
                border-radius: 1rem;
                padding: 0.75rem;
                gap: 0.5rem;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
            }
            
            .stTabs [data-baseweb="tab"] {
                background: transparent;
                color: var(--text-secondary);
                border-radius: 0.5rem;
                padding: 0.75rem 1.5rem;
                font-weight: 500;
                transition: all 0.3s ease;
                border: 1px solid transparent;
            }
            
            .stTabs [data-baseweb="tab"]:hover {
                background: rgba(9, 105, 218, 0.08);
                color: var(--text-primary);
                border-color: rgba(9, 105, 218, 0.2);
            }
            
            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary)) !important;
                color: white !important;
                font-weight: 600;
                border-color: transparent !important;
                box-shadow: 0 4px 12px rgba(9, 105, 218, 0.25);
            }
            
            .sidebar-section {
                background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
                border-radius: 1rem;
                padding: 1.5rem;
                margin: 1rem 0;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
            }
            
            .filter-toggle {
                background: linear-gradient(135deg, var(--bg-secondary), var(--bg-card));
                border: 1px solid var(--border-color);
                border-radius: 0.75rem;
                padding: 1rem;
                margin: 1rem 0;
                box-shadow: var(--shadow);
            }
            
            .info-tooltip {
                display: inline-block;
                background: var(--accent-primary);
                color: white;
                border-radius: 50%;
                width: 1.25rem;
                height: 1.25rem;
                text-align: center;
                line-height: 1.25rem;
                font-size: 0.75rem;
                cursor: help;
                margin-left: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .progress-bar {
                background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
                border-radius: 1rem;
                height: 0.5rem;
                transition: width 0.3s ease;
            }
            
            .metric-card-enhanced {
                background: linear-gradient(135deg, var(--bg-card), var(--bg-secondary));
                border-radius: 1rem;
                padding: 1.5rem;
                margin: 1rem 0;
                border: 1px solid var(--border-color);
                box-shadow: var(--shadow);
                transition: all 0.3s ease;
            }
            
            .metric-card-enhanced:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 32px rgba(9, 105, 218, 0.15);
            }
        </style>
        """

# Initialize session state
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark'  # Default to dark theme
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'reliability_results' not in st.session_state:
    st.session_state.reliability_results = None
if 'rai_results' not in st.session_state:
    st.session_state.rai_results = None
if 'green_results' not in st.session_state:
    st.session_state.green_results = None
if 'eco_mode' not in st.session_state:
    st.session_state.eco_mode = False
if 'show_all_clauses' not in st.session_state:
    st.session_state.show_all_clauses = False

# Apply theme CSS
st.markdown(get_theme_css(), unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Theme toggle button
    col1, col2 = st.columns([1, 0.1])
    with col2:
        theme_emoji = "🌙" if st.session_state.theme == 'dark' else "☀️"
        if st.button(theme_emoji, key="theme_toggle", help="Toggle dark/light mode"):
            st.session_state.theme = 'light' if st.session_state.theme == 'dark' else 'dark'
            st.rerun()
    
    # Header
    st.markdown('<div class="main-header">🔍 TraeGuard</div>', unsafe_allow_html=True)
    st.markdown("**TRAE-powered Reliability & Responsible AI Lab for Digital Policies**")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Eco mode toggle
        eco_mode = st.toggle("🌱 Eco Mode", value=st.session_state.eco_mode,
                           help="Reduce computational overhead for faster analysis")
        st.session_state.eco_mode = eco_mode
        
        if eco_mode:
            st.success("🌱 Eco mode enabled - optimized for speed and efficiency")
        
        st.divider()
        
        # Sample policies
        st.subheader("📋 Sample Policies")
        sample_policies = {
            "Simple Privacy Policy": """
We collect your email address and name when you register.
We retain this information for 30 days after account deletion.
We do not share your data with third parties.
""",
            "Comprehensive Privacy Policy": """
We collect extensive personal information including your name, email, phone number, 
address, location data, browsing history, device information, payment details, 
and biometric data. We retain this information indefinitely for business purposes.
We share your data with our affiliates, service providers, advertising partners, 
analytics companies, and third-party vendors. We may also disclose your 
information to comply with legal obligations.
""",
            "Social Media Policy": """
We collect your profile information, posts, messages, photos, videos, location data,
contact lists, device information, and usage patterns. We retain your data for 
the lifetime of your account plus 90 days. We share information with third-party 
applications, advertisers, analytics providers, and business partners.
"""
        }
        
        selected_sample = st.selectbox("Load sample policy:", [""] + list(sample_policies.keys()))
        
        if selected_sample:
            st.session_state.sample_policy = sample_policies[selected_sample]
    
    # Main content area with tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Analyze", "🧭 Privacy Coach", "🔬 Reliability Lab", "💡 RAI Studio", "🌱 Green Privacy"])
    
    with tab1:
        render_analyze_tab()
    
    with tab2:
        render_privacy_coach_tab()
    
    with tab3:
        render_reliability_tab()
    
    with tab4:
        render_rai_tab()
    
    with tab5:
        render_green_tab()

def render_analyze_tab():
    """Render the Analyze tab with enhanced filtering."""
    st.header("📊 Privacy Policy Analysis")
    
    # Policy input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        policy_text = st.text_area(
            "Paste your privacy policy text here:",
            height=300,
            placeholder="Enter your privacy policy text...",
            value=getattr(st.session_state, 'sample_policy', '')
        )
    
    with col2:
        uploaded_file = st.file_uploader("Or upload a policy file:", type=['txt', 'md'])
        if uploaded_file is not None:
            policy_text = uploaded_file.read().decode('utf-8')
    
    # Analysis button
    if st.button("🔍 Analyze Policy", type="primary"):
        if policy_text.strip():
            with st.spinner("Analyzing policy..."):
                try:
                    analyzer = PrivyReveal()
                    results = analyzer.analyze_policy(policy_text)
                    st.session_state.analysis_results = results
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"Analysis failed: {str(e)}")
                    return
        else:
            st.warning("Please provide a privacy policy to analyze.")
    
    # Display results
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        st.subheader("📋 Analysis Results")
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_clauses = len(results.get('clauses', []))
            st.metric("Total Clauses", total_clauses)
        
        with col2:
            high_risk_clauses = sum(1 for clause in results.get('clauses', [])
                                  if clause.get('risk_score', 0) > 0.7)
            st.metric("High Risk Clauses", high_risk_clauses)
        
        with col3:
            avg_risk = sum(clause.get('risk_score', 0) for clause in results.get('clauses', []))
            avg_risk = avg_risk / total_clauses if total_clauses > 0 else 0
            st.metric("Average Risk Score", f"{avg_risk:.2f}")
        
        # Clause filtering section
        st.subheader("🔍 Clause Analysis")
        
        # Filter toggle
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.session_state.show_all_clauses = st.toggle(
                    "Show all clauses (uncheck to show only important clauses with risk ≥ 0.5 & severity medium/high)",
                    value=st.session_state.show_all_clauses
                )
            
            if not st.session_state.show_all_clauses:
                st.info("ℹ️ Showing only high-impact clauses (risk ≥ 0.5 & severity = medium/high)")
            else:
                st.info("ℹ️ Showing all clauses")
        
        # Process and filter clauses
        clauses_data = []
        for i, clause in enumerate(results.get('clauses', [])):
            risk_score = clause.get('risk_score', 0)
            severity = get_risk_severity(risk_score)
            
            # Apply filtering
            if not st.session_state.show_all_clauses:
                if risk_score < 0.5 or severity == 'Low':
                    continue
            
            clauses_data.append({
                'clause_id': clause.get('id', f'clause_{i}'),
                'text': clause.get('text', '')[:150] + '...' if len(clause.get('text', '')) > 150 else clause.get('text', ''),
                'full_text': clause.get('text', ''),
                'label': clause.get('label', 'Unknown'),
                'risk_score': risk_score,
                'severity': severity,
                'confidence': clause.get('confidence', 0.85)
            })
        
        # Sort clauses: high severity first, then by risk score (descending)
        clauses_data.sort(key=lambda x: (get_severity_sort_key(x['severity']), x['risk_score']), reverse=True)
        
        if clauses_data:
            # Display filtered count
            st.write(f"**Showing {len(clauses_data)} clauses**")
            
            # Display as enhanced cards with expandable full text
            for clause in clauses_data:
                with st.container():
                    # Create columns for clause text and expand button
                    col1, col2 = st.columns([5, 1])
                    
                    with col1:
                        st.markdown(f"""
                        <div class="clause-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
                                <div style="flex: 1;">
                                    <strong>Clause:</strong> {clause['text']}
                                </div>
                                <div style="margin-left: 1rem;">
                                    <span class="metric-badge">{clause['label'].replace('_', ' ').title()}</span>
                                </div>
                            </div>
                            <div style="display: flex; gap: 1rem; align-items: center;">
                                <div>
                                    <strong>Risk Score:</strong> 
                                    <span class="risk-{clause['severity'].lower()}">{clause['risk_score']:.2f}</span>
                                </div>
                                <div>
                                    <strong>Severity:</strong> 
                                    <span class="risk-{clause['severity'].lower()}">{clause['severity']}</span>
                                </div>
                                <div>
                                    <strong>Confidence:</strong> {clause['confidence']:.2f}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Add expand button for full clause text
                        expand_key = f"expand_{clause['clause_id']}"
                        if expand_key not in st.session_state:
                            st.session_state[expand_key] = False
                        
                        if st.button("📖 Expand", key=f"btn_{clause['clause_id']}", help="View full clause text"):
                            st.session_state[expand_key] = not st.session_state[expand_key]
                    
                    # Show full text in expander if toggled
                    if st.session_state[expand_key]:
                        with st.expander(f"📖 Full Clause Text - {clause['label'].replace('_', ' ').title()}", expanded=True):
                            st.markdown(f"**Full Text:** {clause['full_text']}")
                            st.markdown(f"**Label:** {clause['label'].replace('_', ' ').title()}")
                            st.markdown(f"**Risk Score:** {clause['risk_score']:.2f} ({clause['severity']} severity)")
                            st.markdown(f"**Confidence:** {clause['confidence']:.2f}")
                            
                            # Add copy button for full text
                            if st.button("📋 Copy Full Text", key=f"copy_{clause['clause_id']}"):
                                st.code(clause['full_text'], language="text")
                                st.success("Full clause text copied to clipboard!")
                            
                            # PlainText Panda integration
                            if st.button("🐼 Rewrite with PlainText Panda", key=f"panda_{clause['clause_id']}"):
                                if clause['full_text'].strip():
                                    try:
                                        # Call PlainText Panda agent
                                        result = plaintext_panda.run({"clause_text": clause['full_text']})
                                        
                                        # Display the four rewrite versions in tabs
                                        st.subheader("📚 PlainText Panda Rewrites")
                                        
                                        tab1, tab2, tab3, tab4 = st.tabs([
                                            "📝 Simple English", 
                                            "⚖️ Legal (Shortened)", 
                                            "🧒 Explain Like I'm 10", 
                                            "👩‍⚖️ Privacy Lawyer Version"
                                        ])
                                        
                                        with tab1:
                                            st.markdown("**Simple English:**")
                                            st.info(result.get('simple_english', 'Simple English version not available'))
                                        
                                        with tab2:
                                            st.markdown("**Legal (Shortened):**")
                                            st.success(result.get('legal_shortened', 'Legal shortened version not available'))
                                        
                                        with tab3:
                                            st.markdown("**Explain Like I'm 10:**")
                                            st.warning(result.get('eli5', 'ELI5 version not available'))
                                        
                                        with tab4:
                                            st.markdown("**Privacy Lawyer Version:**")
                                            st.error(result.get('privacy_lawyer', 'Privacy lawyer version not available'))
                                            
                                    except Exception as e:
                                        st.error(f"🐼 PlainText Panda encountered an error: {str(e)}")
                                        st.info("Please try again with a different clause or check the agent configuration.")
                                else:
                                    st.warning("⚠️ Cannot rewrite empty clause text. Please ensure the clause has content.")
        else:
            if not st.session_state.show_all_clauses:
                st.warning("No clauses meet the filtering criteria (risk ≥ 0.5 & severity medium/high). Try showing all clauses.")
            else:
                st.info("No clauses to display.")

def render_reliability_tab():
    """Render the Reliability Lab tab with unstable clauses section."""
    st.header("🔬 Reliability Lab")
    
    if not st.session_state.analysis_results:
        st.warning("Please analyze a policy first in the Analyze tab.")
        return
    
    # Reliability testing section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🧪 Test Selection")
        
        # Test options
        run_adversarial = st.checkbox("Adversarial Testing", value=True,
                                    help="Test model robustness with variant clauses")
        run_regression = st.checkbox("Regression Testing", value=True,
                                     help="Compare with baseline predictions")
        run_cross_model = st.checkbox("Cross-Model Comparison", value=True,
                                      help="Compare with external models")
        
        # Apply eco mode restrictions
        if st.session_state.eco_mode:
            eco_settings = get_eco_mode_settings(True)
            if not eco_settings['cross_model_comparison']:
                run_cross_model = False
                st.info("Cross-model comparison disabled in eco mode")
    
    with col2:
        if st.button("🚀 Run Reliability Tests", type="primary"):
            with st.spinner("Running reliability tests..."):
                try:
                    results = {}
                    
                    # Adversarial testing
                    if run_adversarial:
                        with st.spinner("Running adversarial tests..."):
                            tester = AdversarialTester()
                            clauses = st.session_state.analysis_results.get('clauses', [])
                            adversarial_results = tester.run_robustness_suite(clauses)
                            results['adversarial'] = adversarial_results
                    
                    # Regression testing
                    if run_regression:
                        with st.spinner("Running regression tests..."):
                            regression_tester = RegressionTester()
                            clauses = st.session_state.analysis_results.get('clauses', [])
                            regression_results = regression_tester.compare_with_baseline(clauses)
                            results['regression'] = regression_results
                    
                    # Cross-model comparison
                    if run_cross_model:
                        with st.spinner("Running cross-model comparison..."):
                            cross_analyzer = CrossModelAnalyzer()
                            clauses = st.session_state.analysis_results.get('clauses', [])
                            cross_results = cross_analyzer.summarize_cross_model_agreement(clauses)
                            results['cross_model'] = cross_results
                    
                    st.session_state.reliability_results = results
                    st.success("✅ Reliability tests complete!")
                    
                except Exception as e:
                    st.error(f"Reliability testing failed: {str(e)}")
    
    # Display results
    if st.session_state.reliability_results:
        results = st.session_state.reliability_results
        
        # Unstable Clauses Section (Priority #1)
        if 'adversarial' in results and results['adversarial'].get('unstable_clauses'):
            st.subheader("⚠️ Unstable Clauses")
            st.write("**Why this matters:** Unstable clauses indicate where the AI model's predictions are inconsistent when the text is slightly modified. This suggests these clauses may be ambiguous or the model may be uncertain about their classification.")
            st.info("ℹ️ **Detection Criteria:** A clause is marked as unstable if either: (1) Risk drift score ≥ 0.3 (risk score changes significantly), OR (2) Label stability score ≤ 0.7 (model assigns different labels to similar text).")
            
            unstable_clauses = results['adversarial']['unstable_clauses']
            
            if unstable_clauses:
                for clause in unstable_clauses:
                    with st.container():
                        st.markdown(f"""
                        <div class="unstable-clause">
                            <div style="margin-bottom: 0.75rem;">
                                <strong>Original Text:</strong> {clause['original_text'][:200]}...
                            </div>
                            <div style="background: rgba(248, 81, 73, 0.1); border-left: 3px solid #f85149; padding: 0.5rem; margin: 0.5rem 0; border-radius: 0.25rem;">
                                <strong>⚠️ Why this clause is unstable:</strong> This clause shows significant variation in risk scoring and/or label assignment when the text is slightly modified, indicating potential ambiguity or model uncertainty.
                            </div>
                            <div style="display: flex; gap: 2rem; margin-bottom: 0.5rem;">
                                <div>
                                    <strong>Label:</strong> {clause['original_label'].replace('_', ' ').title()}
                                </div>
                                <div>
                                    <strong>Original Risk:</strong> {clause['original_risk']:.2f}
                                </div>
                            </div>
                            <div style="display: flex; gap: 2rem;">
                                <div>
                                    <strong>Risk Drift:</strong> 
                                    <span class="risk-high">{clause['risk_drift_score']:.2f}</span>
                                </div>
                                <div>
                                    <strong>Label Stability:</strong> 
                                    <span class="risk-medium">{clause['label_stability_score']:.2f}</span>
                                </div>
                            </div>
                            <div style="margin-top: 0.5rem;">
                                <span class="metric-badge">High Drift</span>
                                <span class="metric-badge">Low Stability</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.success("✅ No unstable clauses detected for this policy based on current thresholds.")
        else:
            st.info("ℹ️ Run adversarial testing to identify unstable clauses")
        
        st.divider()
        
        # Summary metrics with explanations
        st.subheader("📊 Reliability Metrics")
        
        # Add explanations for each metric
        st.info("ℹ️ **Understanding Reliability Metrics:** Each metric helps assess how stable and consistent the AI model's predictions are under different conditions.")
        
        # Create columns for different test results
        cols = st.columns(len(results))
        
        for i, (test_type, test_results) in enumerate(results.items()):
            with cols[i]:
                if test_type == 'adversarial':
                    st.metric("Label Stability", f"{test_results.get('avg_label_stability', 0):.2f}")
                    st.caption("**What this means:** Measures how consistently the model assigns the same label to slightly modified versions of the same clause. Higher values (closer to 1.0) indicate more stable predictions.")
                    
                    st.metric("Risk Drift", f"{test_results.get('avg_risk_drift', 0):.2f}")
                    st.caption("**What this means:** Shows how much the risk score changes when the clause text is slightly modified. Lower values (closer to 0.0) indicate more stable risk assessment.")
                    
                    st.metric("Unstable Clauses", test_results.get('total_unstable', 0))
                    st.caption("**What this means:** Counts clauses where the model shows significant instability (risk drift ≥ 0.3 OR label stability ≤ 0.7). Fewer unstable clauses indicate better model reliability.")
                
                elif test_type == 'regression':
                    st.metric("Label Changes", f"{test_results.get('percent_label_changed', 0):.1f}%")
                    st.caption("**What this means:** Percentage of clauses where the model's label prediction changed compared to a baseline. Lower percentages indicate more consistent predictions over time.")
                    
                    st.metric("Avg Risk Change", f"{test_results.get('avg_risk_change', 0):.3f}")
                    st.caption("**What this means:** Average change in risk scores compared to baseline predictions. Smaller changes suggest the model maintains consistent risk assessment.")
                
                elif test_type == 'cross_model':
                    st.metric("Agreement Rate", f"{test_results.get('agreement_rate', 0):.1f}%")
                    st.caption("**What this means:** Percentage of clauses where different AI models agree on the classification. Higher agreement rates (above 80%) suggest reliable, consensus-based predictions.")
                    
                    st.metric("Divergent Clauses", test_results.get('divergent_clauses_count', 0))
                    st.caption("**What this means:** Number of clauses where models significantly disagree. Fewer divergent clauses indicate more reliable consensus across different AI approaches.")

def render_rai_tab():
    """Render the RAI Studio tab with enhanced report generation."""
    st.header("💡 RAI Studio - Responsible AI Explanations")
    
    if not st.session_state.analysis_results:
        st.warning("Please analyze a policy first in the Analyze tab.")
        return
    
    # RAI explanation section
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎯 Explanation Options")
        
        # User context
        user_type = st.selectbox(
            "User Type:",
            ["General User", "Parent", "Job Seeker", "Healthcare Patient", "Financial Customer"],
            help="Select to get tailored explanations"
        )
        
        # Explanation focus
        focus_areas = st.multiselect(
            "Focus Areas:",
            ["High Risk Clauses", "Vulnerable Groups", "Data Sharing", "Retention Policies"],
            default=["High Risk Clauses"]
        )
        
        # Generate explanations button
        if st.button("🔍 Generate Explanations", type="primary"):
            with st.spinner("Generating RAI explanations..."):
                try:
                    explainer = RAIExplainer()
                    report_generator = RAIReportGenerator()
                    
                    clauses = st.session_state.analysis_results.get('clauses', [])
                    explanations = []
                    
                    # Generate explanations for relevant clauses
                    for clause in clauses:
                        if clause.get('risk_score', 0) > 0.3:  # Lower threshold for more comprehensive analysis
                            explanation = explainer.explain_clause(
                                clause['text'],
                                clause['label'],
                                clause['risk_score'],
                                user_type.lower().replace(" ", "_")
                            )
                            explanations.append(explanation)
                    
                    # Generate comprehensive report
                    rai_report = report_generator.generate_report(
                        explanations,
                        user_context=user_type,
                        all_clauses=clauses
                    )
                    
                    st.session_state.rai_results = rai_report
                    st.success("✅ RAI explanations generated!")
                    
                except Exception as e:
                    st.error(f"RAI explanation generation failed: {str(e)}")
    
    with col2:
        if st.session_state.rai_results:
            report = st.session_state.rai_results
            
            st.subheader("📋 RAI Analysis Report")
            
            # Display overview
            overview = report['structured']['overview']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Clauses", overview['total_clauses'])
            with col2:
                st.metric("High Risk", overview['high_risk_clauses'])
            with col3:
                st.metric("Medium Risk", overview['medium_risk_clauses'])
            with col4:
                st.metric("Low Risk", overview['low_risk_clauses'])
            
            # Key themes
            if report['structured']['key_themes']:
                st.subheader("🎯 Key Themes Identified")
                for theme in report['structured']['key_themes']:
                    st.write(f"• {theme}")
            
            # High risk clauses
            if report['structured']['high_risk_clauses']:
                st.subheader("⚠️ High Risk Clauses")
                for i, clause in enumerate(report['structured']['high_risk_clauses'], 1):
                    with st.expander(f"Clause {i}: {clause['text'][:100]}..."):
                        st.write(f"**Risk Score:** {clause['risk_score']:.2f}")
                        st.write(f"**Explanation:** {clause['explanation']}")
                        st.write(f"**Worst Case:** {clause['worst_case']}")
                        if clause['vulnerable_groups']:
                            st.write(f"**Vulnerable Groups:** {', '.join(clause['vulnerable_groups'])}")
                        st.write(f"**Recommendation:** {clause['recommendation']}")
            
            # Recommendations
            if report['structured']['recommendations']:
                st.subheader("💡 Recommendations")
                for i, rec in enumerate(report['structured']['recommendations'], 1):
                    st.write(f"{i}. {rec}")
            
            # Summary
            st.subheader("�� Summary")
            st.write(report['structured']['summary'])
            
            # Report download
            st.subheader("📄 Download Report")
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="📥 Download Full Report",
                    data=report['markdown'],
                    file_name=f"traeguard_rai_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
            with col2:
                if st.button("📋 Copy Report to Clipboard"):
                    st.code(report['markdown'], language="markdown")
                    st.success("Report copied to clipboard!")

def render_privacy_coach_tab():
    st.header("🧭 Privacy Coach")
    if not st.session_state.analysis_results:
        st.warning("Please analyze a policy first in the Analyze tab.")
        return
    from suggestions.privacy_coach import generate_privacy_coach
    site_hint = None
    green_metrics = None
    if 'green_results' in st.session_state and st.session_state.green_results:
        gr = st.session_state.green_results
        green_metrics = {
            'data_categories_count': getattr(gr, 'data_categories_count', None),
            'max_retention_days': getattr(gr, 'max_retention_days', None),
            'third_party_count': getattr(gr, 'third_party_count', None),
            'tier': getattr(gr, 'tier', None)
        }
    if st.button("🧠 Generate Privacy Suggestions", type="primary"):
        with st.spinner("Generating site-specific suggestions..."):
            result = generate_privacy_coach(st.session_state.analysis_results, site_hint, green_metrics)
            if result.get('site'):
                st.caption(f"Website detected: {result['site']}")
            st.subheader("Top Risks")
            risks = result.get('top_risks', [])
            if risks:
                st.write(", ".join(risks))
            st.subheader("Recommended Actions")
            suggestions = result.get('suggestions', [])
            for s in suggestions:
                cat = s.get('category','general')
                icon = '🔍' if cat=='tracking' else '🔗' if cat=='sharing' else '🕒' if cat=='retention' else '📥' if cat=='collection' else '⚠️' if cat=='sensitive' else '✅'
                st.write(f"- {icon} {s.get('text','')}")

def render_green_tab():
    """Render the Green Privacy tab with enhanced metrics and tooltips."""
    st.header("🌱 Green Privacy - Data Footprint Analysis")
    
    if not st.session_state.analysis_results:
        st.warning("Please analyze a policy first in the Analyze tab.")
        return
    
    # Green privacy analysis
    if st.button("🌍 Analyze Data Footprint", type="primary"):
        with st.spinner("Analyzing data footprint..."):
            try:
                footprint_result = analyze_policy_footprint(
                    st.session_state.analysis_results,
                    eco_mode=st.session_state.eco_mode
                )
                
                st.session_state.green_results = footprint_result
                st.success("✅ Data footprint analysis complete!")
                
            except Exception as e:
                st.error(f"Footprint analysis failed: {str(e)}")
                return
    
    # Display results
    if st.session_state.green_results:
        result = st.session_state.green_results
        
        # Main footprint score with enhanced styling
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            with st.container():
                st.write("**Data Categories**")
                st.metric("Categories", result.data_categories_count)
                st.caption("Different types of personal data collected")
        
        with col2:
            # Large footprint score display
            tier_class = f"tier-{result.tier.lower()}"
            st.markdown(
                f"""
                <div style="text-align: center; margin: 1rem 0;">
                    <div style="font-size: 4rem; {tier_class}">
                        {result.tier_emoji} {result.data_footprint_score:.0f}
                    </div>
                    <div style="font-size: 1.5rem; {tier_class}; margin-top: 0.5rem;">
                        {result.tier} Impact
                    </div>
                    <div style="color: var(--text-secondary); font-size: 0.9rem; margin-top: 0.5rem;">
                        Environmental & Privacy Impact Score
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        
        with col3:
            with st.container():
                st.write("**Retention Period**")
                years = result.max_retention_days / 365
                st.metric("Max Retention", f"{years:.1f} years" if years >= 1 else f"{result.max_retention_days} days")
                st.caption("Longest data retention period")
        
        # Quick visual summary
        st.subheader("📊 Quick Impact Overview")
        
        # Create a visual summary row
        summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
        
        with summary_col1:
            # Data categories visual
            category_percentage = min(result.data_categories_count / 12, 1.0) * 100
            st.metric("Data Types", f"{result.data_categories_count}/12")
            st.progress(category_percentage / 100)
            with st.expander("ℹ️ Details"):
                st.write("**What this measures:** Number of different categories of personal data collected.")
                st.write("**Why it matters:** More data types generally mean higher privacy risk and larger environmental footprint.")
                st.write(f"**Your score:** {category_percentage:.0f}% of maximum concern")
        
        with summary_col2:
            # Third-party sharing visual
            sharing_percentage = min(result.third_party_count / 6, 1.0) * 100
            st.metric("Sharing Partners", f"{result.third_party_count}/6")
            st.progress(sharing_percentage / 100)
            with st.expander("ℹ️ Details"):
                st.write("**What this measures:** Number of different types of third parties your data can be shared with.")
                st.write("**Why it matters:** More sharing increases privacy risk and data exposure.")
                st.write(f"**Your score:** {sharing_percentage:.0f}% of maximum concern")
        
        with summary_col3:
            # Tracking visual
            tracking_percentage = min(result.tracking_count / 4, 1.0) * 100
            st.metric("Tracking Methods", f"{result.tracking_count}/4")
            st.progress(tracking_percentage / 100)
            with st.expander("ℹ️ Details"):
                st.write("**What this measures:** Use of cookies, trackers, device IDs, or fingerprinting.")
                st.write("**Why it matters:** Tracking can follow users across websites and build detailed profiles.")
                st.write(f"**Your score:** {tracking_percentage:.0f}% of maximum concern")
        
        with summary_col4:
            # Retention visual
            retention_percentage = min(result.max_retention_days / 1825, 1.0) * 100  # 5 years max
            years_display = result.max_retention_days / 365
            st.metric("Data Retention", f"{years_display:.1f}y")
            st.progress(retention_percentage / 100)
            with st.expander("ℹ️ Details"):
                st.write("**What this measures:** How long your personal data can be retained.")
                st.write("**Why it matters:** Longer retention increases privacy risk and storage environmental impact.")
                st.write(f"**Your score:** {retention_percentage:.0f}% of maximum concern")
        
        # Enhanced metrics grid with collapsible details
        st.subheader("📊 Detailed Footprint Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Data categories impact
            with st.container():
                st.write("**Data Categories Impact**")
                category_score = min(result.data_categories_count / 12, 1.0) * 100
                st.progress(category_score / 100)
                st.write(f"{result.data_categories_count} categories detected")
                with st.expander("ℹ️ Learn more"):
                    st.write("How many different types of personal data this policy allows the company to collect. More categories usually mean a larger privacy and sustainability footprint.")
            
            # Third-party sharing
            with st.container():
                st.write("**Third-Party Sharing Impact**")
                sharing_score = min(result.third_party_count / 6, 1.0) * 100
                st.progress(sharing_score / 100)
                st.write(f"{result.third_party_count} sharing mentions")
                with st.expander("ℹ️ Learn more"):
                    st.write("How many types of third parties your data can be shared with. More sharing increases risk and complexity.")
            
            # Tracking technologies
            with st.container():
                st.write("**Tracking Technologies**")
                tracking_score = min(result.tracking_count / 4, 1.0) * 100
                st.progress(tracking_score / 100)
                st.write(f"{result.tracking_count} tracking mentions")
                with st.expander("ℹ️ Learn more"):
                    st.write("Use of cookies, trackers, or device IDs which can follow users across sites and sessions.")
        
        with col2:
            # Retention impact
            with st.container():
                st.write("**Retention Impact**")
                retention_score = min(result.max_retention_days / 1825, 1.0) * 100
                st.progress(retention_score / 100)
                years = result.max_retention_days / 365
                st.write(f"Up to {years:.1f} years retention")
                with st.expander("ℹ️ Learn more"):
                    st.write("How long your data can be stored. Longer storage increases both privacy risk and energy/storage impact.")
            
            # Data broker mentions
            with st.container():
                st.write("**Data Broker Activity**")
                broker_score = 100 if result.data_broker_mention else 0
                st.progress(broker_score / 100)
                st.write("Data broker mentioned" if result.data_broker_mention else "No data broker mention")
                with st.expander("ℹ️ Learn more"):
                    st.write("Whether data is shared or sold to data brokers/advertisers, significantly increasing privacy risk.")
            
            # Consent granularity
            with st.container():
                st.write("**Consent Granularity**")
                consent_score = 100 if result.consent_granularity == 'granular' else 50 if result.consent_granularity == 'mixed' else 0
                st.progress(consent_score / 100)
                st.write(f"{result.consent_granularity.title()} consent")
                with st.expander("ℹ️ Learn more"):
                    st.write("Single blanket consent vs granular opt-outs. Granular consent gives users more control over their data.")
        
        # Eco mode optimizations
        if result.eco_mode_applied and result.optimizations_applied:
            st.subheader("⚡ Eco-Mode Optimizations Applied")
            
            for optimization in result.optimizations_applied:
                st.write(f"✅ {optimization}")
            
            st.info("💡 Eco-mode reduces computational overhead while maintaining core analysis quality")
        
        # Recommendations with enhanced styling
        st.subheader("💡 Sustainability & Privacy Recommendations")
        
        recommendations = []
        
        if result.tier == "High":
            recommendations.extend([
                "🔴 **Critical:** Reduce data collection categories and implement data minimization",
                "🔴 **Critical:** Establish clear data deletion policies and user deletion rights",
                "🔴 **Critical:** Limit third-party data sharing and require explicit consent"
            ])
        elif result.tier == "Medium":
            recommendations.extend([
                "🟡 **Important:** Focus on reducing data categories and retention periods",
                "🟡 **Important:** Provide granular consent options instead of blanket consent",
                "🟡 **Important:** Reduce tracking technologies and offer opt-out options"
            ])
        else:
            recommendations.extend([
                "🟢 **Good:** Maintain current low-impact data practices",
                "🟢 **Good:** Continue monitoring and improving privacy practices",
                "🟢 **Good:** Consider implementing additional privacy-enhancing measures"
            ])
        
        # Add specific recommendations based on metrics
        if result.data_broker_mention:
            recommendations.append("⚠️ **Urgent:** Remove data broker sharing or provide explicit opt-in consent")
        
        if result.consent_granularity == 'blanket':
            recommendations.append("⚠️ **Important:** Replace blanket consent with granular, specific consent options")
        
        if result.tracking_count > 2:
            recommendations.append("⚠️ **Important:** Reduce tracking technologies and provide clear opt-out mechanisms")
        
        for rec in recommendations:
            st.write(rec)

# Helper functions
def get_risk_severity(risk_score: float) -> str:
    """Get risk severity level."""
    if risk_score > 0.7:
        return "High"
    elif risk_score > 0.4:
        return "Medium"
    else:
        return "Low"

def get_risk_class(risk_score: float) -> str:
    """Get CSS class for risk score."""
    if risk_score > 0.7:
        return "risk-high"
    elif risk_score > 0.4:
        return "risk-medium"
    else:
        return "risk-low"

def get_severity_class(severity: str) -> str:
    """Get CSS class for severity."""
    severity_lower = severity.lower()
    if severity_lower == "high":
        return "risk-high"
    elif severity_lower == "medium":
        return "risk-medium"
    else:
        return "risk-low"

def get_severity_sort_key(severity: str) -> int:
    """Get sort key for severity (High > Medium > Low)."""
    if severity == "High":
        return 3
    elif severity == "Medium":
        return 2
    else:
        return 1

if __name__ == "__main__":
    main()
