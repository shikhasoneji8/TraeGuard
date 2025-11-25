import streamlit as st
import pandas as pd
from datetime import datetime
from green.footprint import analyze_policy_footprint

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
    st.write('Reliability analysis coming soon.')

with tabs[3]:
    st.write('TraeGuard helps analyze privacy policies for risk, sharing, retention, and footprint.')