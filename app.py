import streamlit as st
import json
import os
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="Myntra Wishlist Discovery | 10 Core Research Questions",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Custom Styling ---
st.markdown("""
<style>
    /* Global Container */
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1050px;
    }
    
    /* Header Card */
    .hero-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        color: #ffffff;
    }
    .hero-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 8px;
        color: #f8fafc;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        line-height: 1.5;
    }
    
    /* Stats Bar */
    .stats-bar {
        display: flex;
        gap: 16px;
        margin-top: 16px;
    }
    .stat-pill {
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #38bdf8;
    }
    
    /* Badge styling */
    .rq-badge {
        display: inline-block;
        background-color: #ec4899;
        color: white;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 6px;
        margin-bottom: 6px;
    }
    .data-pill {
        display: inline-block;
        background-color: #0284c7;
        color: white;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 12px;
        margin-left: 8px;
    }
    
    /* Answer Box */
    .answer-box {
        background-color: #0f172a;
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 20px 24px;
        margin: 14px 0 20px 0;
        color: #e2e8f0;
        line-height: 1.6;
    }
    
    /* Verbatim Review Box */
    .review-box {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 12px;
    }
    .review-text {
        font-size: 0.92rem;
        color: #f8fafc;
        font-style: italic;
        line-height: 1.5;
    }
    .review-meta {
        font-size: 0.78rem;
        color: #94a3b8;
        margin-top: 6px;
    }
    .source-tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        background-color: #334155;
        color: #e2e8f0;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

def sanitize_answer(text):
    if not text:
        return ""
    # Strip any think tags or prompt instructions if ever present
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'think>.*?(###|\Z)', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'Thinking Process:.*?(###|\Z)', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'Deconstruct the Request:.*?(###|\Z)', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'Role:.*?Output Structure:.*?(###|\Z)', r'\1', text, flags=re.DOTALL)
    return text.strip()

# --- Load Data Directly ---
def load_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "backend", "rq_insights.json")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure every item is clean
            for k, v in data.items():
                v["ai_answer"] = sanitize_answer(v.get("ai_answer", ""))
            return data
    return {}

insights_data = load_data()
total_reviews = 2226
base_dir = os.path.dirname(os.path.abspath(__file__))
collected_path = os.path.join(base_dir, "collected_data.json")
if os.path.exists(collected_path):
    try:
        with open(collected_path, "r", encoding="utf-8") as f:
            total_reviews = len(json.load(f))
    except Exception:
        pass

# --- Header ---
st.markdown(f"""
<div class="hero-header">
    <div class="hero-title">🛍️ Myntra Wishlist Conversion Discovery Engine</div>
    <div class="hero-subtitle">
        Customer discovery findings and answers for all 10 core research questions determined directly from real customer reviews across Play Store, App Store, Twitter/X, YouTube, and Reddit.
    </div>
    <div class="stats-bar">
        <span class="stat-pill">📊 Total Customer Reviews: {total_reviews:,}</span>
        <span class="stat-pill">🎯 10 Core Research Questions</span>
        <span class="stat-pill">🌐 5 Data Platforms Analyzed</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- Render Questions & Answers ---
for q_key in sorted(insights_data.keys(), key=lambda x: int(x)):
    q_data = insights_data[q_key]
    
    expander_title = f"RQ {q_data['number']}: {q_data['title']}  —  [{q_data['data_count']} backing reviews]"
    with st.expander(expander_title, expanded=(q_data['number'] == 1)):
        st.markdown(f"<span class='rq-badge'>QUESTION {q_data['number']}</span> <span class='data-pill'>📊 Backed by {q_data['data_count']} customer reviews ({q_data['data_ratio']}% of total dataset)</span>", unsafe_allow_html=True)
        
        # 1. Answer First
        st.markdown("#### 💡 Answer (Determined from Customer Reviews)")
        st.markdown(f"<div class='answer-box'>{q_data.get('ai_answer', '')}</div>", unsafe_allow_html=True)
        
        # 2. Backing Reviews Second
        reviews = q_data.get("backing_reviews", [])
        st.markdown(f"#### 💬 Customer Reviews Backing This Answer ({len(reviews)} reviews):")
        
        for r in reviews:
            source = r.get("source", "Review")
            platform = r.get("platform", source)
            date = r.get("date", "N/A")
            segment = r.get("segment", "unidentified")
            
            st.markdown(f"""
            <div class="review-box">
                <div class="review-text">"{r.get('raw_text')}"</div>
                <div class="review-meta">
                    <span class="source-tag">{platform}</span>
                    <span>📅 {date}</span> | 
                    <span>👤 Segment: {segment}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Myntra Growth PM Discovery Engine • 10 Research Questions Analysis based on 2,226 Multi-Platform Customer Reviews")
