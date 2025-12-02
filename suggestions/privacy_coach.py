from typing import Dict, List, Any, Optional
import re
import urllib.parse

def _domain_from_text(text: str) -> Optional[str]:
    urls = re.findall(r'(https?://[^\s)"<>]+|www\.[^\s)"<>]+)', text)
    emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    if urls:
        u0 = urls[0]
        if not u0.startswith('http'):
            u0 = 'http://' + u0
        try:
            return urllib.parse.urlparse(u0).netloc
        except Exception:
            return None
    if emails:
        try:
            return emails[0].split('@')[1]
        except Exception:
            return None
    return None

def _top_risk_themes(clauses: List[Dict[str, Any]]) -> List[str]:
    scores = { 'tracking': 0.0, 'data_sharing': 0.0, 'data_retention': 0.0, 'data_collection': 0.0, 'sensitive': 0.0 }
    for c in clauses:
        label = c.get('label', '')
        rs = float(c.get('risk_score', 0.0))
        if label in scores:
            scores[label] += rs
        tl = c.get('text', '').lower()
        if any(w in tl for w in ['biometric','health','financial','ssn','passport']):
            scores['sensitive'] += rs
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [k for k, v in ranked if v > 0][:5]

def _theme_suggestions(theme: str, site: Optional[str], metrics: Dict[str, Any]) -> List[Dict[str, str]]:
    name = site or "this site"
    sugg = []
    if theme == 'tracking':
        sugg.append({ 'category': 'tracking', 'text': f"On {name}, set cookies to 'Essential only' in the cookie/preferences page." })
        sugg.append({ 'category': 'tracking', 'text': f"Disable cross-site tracking for {name} in your browser and app settings." })
    elif theme == 'data_sharing':
        sugg.append({ 'category': 'sharing', 'text': f"On {name}, turn off ad personalization and partner sharing in account privacy settings." })
        sugg.append({ 'category': 'sharing', 'text': f"Use the 'Do Not Sell or Share' link on {name} if available." })
    elif theme == 'data_retention':
        sugg.append({ 'category': 'retention', 'text': f"Periodically delete data on {name} via the privacy/requests portal." })
        sugg.append({ 'category': 'retention', 'text': f"Close unused {name} accounts to reduce long-term retention." })
    elif theme == 'data_collection':
        sugg.append({ 'category': 'collection', 'text': f"Provide only required fields on {name}; skip optional phone/location where possible." })
        sugg.append({ 'category': 'collection', 'text': f"Use an email alias for {name} to limit identity linking." })
    elif theme == 'sensitive':
        sugg.append({ 'category': 'sensitive', 'text': f"Avoid uploading biometrics or health details to {name}; request removal if already provided." })
    return sugg

def _extract_action_links(text: str) -> List[Dict[str, str]]:
    links = []
    urls = re.findall(r'(https?://[^\s)"<>]+|www\.[^\s)"<>]+)', text)
    for u in urls:
        lu = u.lower()
        if 'do-not-sell' in lu or 'donotsell' in lu or 'do_not_sell' in lu:
            links.append({ 'category': 'sharing', 'text': f"Go to {u} to submit 'Do Not Sell or Share'" })
        elif 'opt-out' in lu or 'optout' in lu or 'unsubscribe' in lu:
            links.append({ 'category': 'sharing', 'text': f"Visit {u} to opt out of marketing or sharing" })
        elif 'cookie' in lu or 'consent' in lu or 'preferences' in lu:
            links.append({ 'category': 'tracking', 'text': f"Open {u} to adjust cookie and consent settings" })
        elif 'privacy' in lu and any(k in lu for k in ['request','portal','rights','access','delete','erasure','dsar']):
            links.append({ 'category': 'rights', 'text': f"Use {u} to submit privacy requests (access/deletion)" })
    return links

def generate_privacy_coach(analysis: Dict[str, Any], site_hint: Optional[str], green: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    clauses = analysis.get('clauses', []) if analysis else []
    full_text = analysis.get('full_text', '') if analysis else ''
    site = site_hint or _domain_from_text(full_text or " ".join([c.get('text','') for c in clauses]))
    themes = _top_risk_themes(clauses)
    suggestions: List[Dict[str, str]] = []
    for t in themes:
        suggestions.extend(_theme_suggestions(t, site, green or {}))
    suggestions.extend(_extract_action_links(full_text or " ".join([c.get('text','') for c in clauses])))
    top_risks = themes
    overall_summary = f"Top risks on {site or 'this site'}: " + ", ".join(top_risks) if top_risks else "Risks not detected"
    return {
        'site': site,
        'overall_summary': overall_summary,
        'top_risks': top_risks,
        'suggestions': suggestions[:10]
    }