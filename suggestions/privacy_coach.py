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

def _detect_categories(clauses: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    cats: Dict[str, List[Dict[str, Any]]] = {
        'tracking': [],
        'third_party_sharing': [],
        'sensitive_collection': [],
        'long_term_retention': [],
        'profiling': [],
        'cross_device': [],
        'ad_tech': [],
        'weak_controls': [],
        'invasive_permissions': [],
        'unclear_wording': []
    }
    for c in clauses:
        t = c.get('text', '').lower()
        if c.get('label') == 'tracking' or any(w in t for w in ['cookie','track','fingerprint','device id','telemetry']):
            cats['tracking'].append(c)
        if c.get('label') == 'data_sharing' or any(w in t for w in ['third','partners','affiliates','vendors','advertisers','analytics']):
            cats['third_party_sharing'].append(c)
        if any(w in t for w in ['biometric','health','medical','financial','ssn','passport','precise location']):
            cats['sensitive_collection'].append(c)
        if c.get('label') == 'data_retention' or any(w in t for w in ['retain','store','archive','indefinite','permanent','years']):
            cats['long_term_retention'].append(c)
        if any(w in t for w in ['profile','personalize','targeted advertising','segmentation','inference']):
            cats['profiling'].append(c)
        if any(w in t for w in ['cross-device','merge data','combine data','device graph']):
            cats['cross_device'].append(c)
        if any(w in t for w in ['google analytics','meta pixel','adtech','advertising partners','programmatic']):
            cats['ad_tech'].append(c)
        if any(w in t for w in ['may', 'might', 'we may', 'from time to time']) and not any(w in t for w in ['opt-out','opt out','unsubscribe','settings']):
            cats['weak_controls'].append(c)
        if any(w in t for w in ['camera','microphone','contacts','location permission']):
            cats['invasive_permissions'].append(c)
        if any(w in t for w in ['as permitted by law','legitimate interests','necessary for','other purposes']):
            cats['unclear_wording'].append(c)
    return cats

def _extract_links_and_contacts(text: str) -> Dict[str, List[str]]:
    urls = re.findall(r'(https?://[^\s)"<>]+|www\.[^\s)"<>]+)', text)
    emails = re.findall(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    phones = re.findall(r'\+?\d[\d\-\s\(\)]{7,}', text)
    return { 'urls': urls, 'emails': emails, 'phones': phones }

def _make_suggestion(site: Optional[str], clause: Dict[str, Any], action_text: str, link: Optional[str]) -> Dict[str, str]:
    name = site or 'this site'
    snippet = clause.get('text','')[:220]
    if link:
        return { 'category': clause.get('label','general'), 'text': f"On {name}, {action_text} ({link})", 'evidence': snippet }
    return { 'category': clause.get('label','general'), 'text': f"On {name}, {action_text}", 'evidence': snippet }

def generate_privacy_coach(analysis: Dict[str, Any], site_hint: Optional[str], green: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    clauses = analysis.get('clauses', []) if analysis else []
    full_text = analysis.get('full_text', '') if analysis else ''
    site = site_hint or _domain_from_text(full_text or " ".join([c.get('text','') for c in clauses]))
    cats = _detect_categories(clauses)
    contacts = _extract_links_and_contacts(full_text or " ".join([c.get('text','') for c in clauses]))
    suggestions: List[Dict[str, str]] = []
    top_risks = [k for k, v in cats.items() if len(v) > 0]
    for cl in cats['tracking'][:3]:
        link = next((u for u in contacts['urls'] if any(x in u.lower() for x in ['cookie','consent','preferences'])), None)
        suggestions.append(_make_suggestion(site, cl, "set cookies to 'Essential only' and turn off tracking", link))
    for cl in cats['third_party_sharing'][:3]:
        link = next((u for u in contacts['urls'] if any(x in u.lower() for x in ['privacy','request','rights']) and any(y in u.lower() for y in ['sharing','sell'])), None)
        suggestions.append(_make_suggestion(site, cl, "disable partner sharing and advertising personalization in account privacy settings", link))
    for cl in cats['long_term_retention'][:3]:
        link = next((u for u in contacts['urls'] if any(x in u.lower() for x in ['privacy','request','delete','erasure'])), None)
        suggestions.append(_make_suggestion(site, cl, "submit a deletion request and periodically remove stored data", link))
    for cl in cats['sensitive_collection'][:2]:
        suggestions.append(_make_suggestion(site, cl, "avoid providing sensitive data and request removal of any uploads", None))
    for cl in cats['profiling'][:2]:
        suggestions.append(_make_suggestion(site, cl, "turn off ad personalization and profiling in settings", None))
    for cl in cats['cross_device'][:2]:
        suggestions.append(_make_suggestion(site, cl, "sign out on unused devices and avoid cross-account linking", None))
    for cl in cats['ad_tech'][:2]:
        suggestions.append(_make_suggestion(site, cl, "opt out of advertising integrations and clear tracking history", None))
    for cl in cats['weak_controls'][:2]:
        link = next((u for u in contacts['urls'] if 'settings' in u.lower() or 'preferences' in u.lower()), None)
        suggestions.append(_make_suggestion(site, cl, "use account privacy settings to explicitly opt out of optional processing", link))
    for cl in cats['invasive_permissions'][:2]:
        suggestions.append(_make_suggestion(site, cl, "revoke app permissions like camera, microphone, contacts, and precise location", None))
    for cl in cats['unclear_wording'][:2]:
        email = next(iter(contacts['emails']), None)
        suggestions.append(_make_suggestion(site, cl, "ask the privacy team to clarify vague purposes and obtain explicit consent", email))
    overall_summary = (f"Top risks on {site or 'this site'}: " + ", ".join(top_risks)) if top_risks else "Risks not detected"
    return { 'site': site, 'overall_summary': overall_summary, 'top_risks': top_risks, 'suggestions': suggestions[:12] }