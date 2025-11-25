import streamlit as st
import pandas as pd
from datetime import datetime
from green.footprint import analyze_policy_footprint
import re
import random

def analyze_policy(policy_text: str):
    clauses = [c.strip() for c in policy_text.split('.') if c.strip()]
    results = []
    for i, text in enumerate(clauses):
        risk = 0.3
        tl = text.lower()
        if 'collect' in tl and 'personal' in tl:
            risk += 0.4
        if 'share' in tl or 'third party' in tl:
            risk += 0.3
        if 'retain' in tl and ('indefinite' in tl or 'permanent' in tl):
            risk += 0.2
        if 'sell' in tl or 'monetize' in tl:
            risk += 0.3
        if 'track' in tl or 'monitor' in tl:
            risk += 0.2
        risk = min(risk, 1.0)
        if 'collect' in tl:
            label = 'data_collection'
        elif 'share' in tl or 'third party' in tl:
            label = 'data_sharing'
        elif 'retain' in tl or 'store' in tl:
            label = 'data_retention'
        elif 'track' in tl or 'monitor' in tl:
            label = 'tracking'
        else:
            label = 'general'
        results.append({
            'id': f'clause_{i}',
            'text': text,
            'label': label,
            'risk_score': risk,
            'confidence': 0.85
        })
    return results

def generate_report(clauses, user_context: str):
    high = [c for c in clauses if c['risk_score'] > 0.7]
    medium = [c for c in clauses if 0.4 < c['risk_score'] <= 0.7]
    themes = []
    texts = [c['text'].lower() for c in clauses]
    if any('collect' in t and 'personal' in t for t in texts):
        themes.append('Extensive personal data collection')
    if any('share' in t or 'third party' in t for t in texts):
        themes.append('Broad third-party data sharing')
    if any('retain' in t and ('indefinite' in t or 'permanent' in t) for t in texts):
        themes.append('Indefinite data retention')
    if any('track' in t or 'monitor' in t for t in texts):
        themes.append('Behavioral tracking and monitoring')
    overview = {
        'total_clauses': len(clauses),
        'high_risk_clauses': len(high),
        'medium_risk_clauses': len(medium),
        'low_risk_clauses': len(clauses) - len(high) - len(medium),
        'user_context': user_context,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    summary = f"This privacy policy contains {len(high)+len(medium)} clauses that pose potential privacy risks. "
    if high:
        summary += f"{len(high)} clauses are classified as high-risk and require immediate attention. "
    if medium:
        summary += f"{len(medium)} clauses present medium-level risks that should be monitored. "
    if themes:
        summary += f"Key concerns include: {', '.join(themes[:2])}."
    return overview, themes or ['Standard data processing practices'], summary

st.set_page_config(page_title='TraeGuard', layout='wide')
st.title('TraeGuard – Privacy Policy Analysis')

with st.sidebar:
    st.header('Settings')
    ctx = st.selectbox('User context', ['general','children','elderly','job_seeker','healthcare_patient','financial_customer'], index=0)
    theme_choice = st.selectbox('Theme', ['Light','Dark'], index=0)
    eco_mode = st.checkbox('Eco mode', value=False)

if theme_choice == 'Dark':
    st.markdown(
        """
        <style>
        .stApp { background-color: #0e1117; color: #fafafa; }
        .stMarkdown, .stText, .stDataFrame, .stMetric { color: #fafafa; }
        div[data-testid="stMetricDelta"] { color: #fafafa; }
        </style>
        """,
        unsafe_allow_html=True,
    )

policy = st.text_area('Paste privacy policy text', height=240)
tabs = st.tabs(['Analyze','Green Footprint','Reliability','About'])

with tabs[0]:
    if st.button('Analyze'):
        clauses = analyze_policy(policy)
        df = pd.DataFrame(clauses)
        st.subheader('Detected Clauses')
        st.dataframe(df[['id','label','risk_score','text']], use_container_width=True)
        overview, themes, summary = generate_report(clauses, ctx)
        st.subheader('Overview')
        col1, col2, col3 = st.columns(3)
        col1.metric('Total Clauses', overview['total_clauses'])
        col2.metric('High Risk', overview['high_risk_clauses'])
        col3.metric('Medium Risk', overview['medium_risk_clauses'])
        st.subheader('Key Themes')
        for t in themes:
            st.write(f'- {t}')
        st.subheader('Summary')
        st.write(summary)

with tabs[1]:
    st.write('Estimate environmental footprint and third-party exposure from the policy.')
    if st.button('Calculate Footprint'):
        if policy.strip():
            summary = analyze_policy_footprint(policy, eco_mode)
            col1, col2, col3 = st.columns(3)
            col1.metric('Footprint Score', summary.data_footprint_score)
            col2.metric('Tier', summary.tier)
            col3.metric('Retention (days)', summary.max_retention_days)
            st.write(f"Data categories: {summary.data_categories_count}")
            st.write(f"Third-party mentions: {summary.third_party_count}")
            if eco_mode and summary.optimizations_applied:
                st.write('Optimizations applied:')
                for opt in summary.optimizations_applied:
                    st.write(f'- {opt}')
        else:
            st.write('Enter policy text above to calculate footprint.')

with tabs[2]:
    st.write('Test how clause classification behaves under simple text variations.')
    def _paraphrase_clause(text: str) -> str:
        replacements = {
            'collect': ['gather','acquire'],
            'share': ['disclose','provide'],
            'retain': ['store','keep'],
            'sell': ['trade','monetize'],
            'track': ['monitor','observe']
        }
        tl = text.lower()
        for k, vals in replacements.items():
            if k in tl:
                rep = random.choice(vals)
                tl = tl.replace(k, rep)
        return tl
    def _negate_clause(text: str) -> str:
        tl = text
        tl = re.sub(r'\bwill\b', 'will not', tl, flags=re.IGNORECASE)
        tl = re.sub(r'\bmay\b', 'may not', tl, flags=re.IGNORECASE)
        return tl
    def _ambiguous_clause(text: str) -> str:
        tl = re.sub(r'\b\d+\s+days?\b', 'a reasonable period', text, flags=re.IGNORECASE)
        tl = re.sub(r'\b\d+\s+months?\b', 'some months', tl, flags=re.IGNORECASE)
        tl = re.sub(r'\b\d+\s+years?\b', 'some years', tl, flags=re.IGNORECASE)
        return tl
    if st.button('Run Reliability'):
        if not policy.strip():
            st.write('Enter policy text above to run reliability tests.')
        else:
            clauses = analyze_policy(policy)
            variants_metrics = []
            for c in clauses[:10]:
                base = c
                p_var = _paraphrase_clause(c['text'])
                n_var = _negate_clause(c['text'])
                a_var = _ambiguous_clause(c['text'])
                res_p = analyze_policy(p_var)[0]
                res_n = analyze_policy(n_var)[0]
                res_a = analyze_policy(a_var)[0]
                def drift(v):
                    return abs(v['risk_score'] - base['risk_score']) / max(base['risk_score'], 1.0)
                metrics = {
                    'id': base['id'],
                    'label': base['label'],
                    'risk': base['risk_score'],
                    'paraphrase_drift': drift(res_p),
                    'negation_drift': drift(res_n),
                    'ambiguous_drift': drift(res_a),
                    'label_stability_paraphrase': int(res_p['label'] == base['label']),
                    'label_stability_negation': int(res_n['label'] == base['label']),
                    'label_stability_ambiguous': int(res_a['label'] == base['label'])
                }
                variants_metrics.append(metrics)
            dfm = pd.DataFrame(variants_metrics)
            st.subheader('Variant Stability Metrics')
            st.dataframe(dfm, use_container_width=True)
            avg_drift = dfm[['paraphrase_drift','negation_drift','ambiguous_drift']].mean().mean()
            label_stab = dfm[[
                'label_stability_paraphrase','label_stability_negation','label_stability_ambiguous'
            ]].mean().mean()
            c1,c2 = st.columns(2)
            c1.metric('Avg risk drift', f"{avg_drift:.2f}")
            c2.metric('Avg label stability', f"{label_stab:.2f}")

with tabs[3]:
    st.write('TraeGuard helps analyze privacy policies for risk, sharing, retention, reliability, and green footprint.')
    st.write('Use Analyze to classify clauses, Green Footprint to estimate environmental impact, and Reliability to test robustness.')