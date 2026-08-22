import streamlit as st
import json
import os

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
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1100px;
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
    
    /* Question Card Header */
    .rq-badge {
        display: inline-block;
        background-color: #ec4899;
        color: white;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .data-pill {
        display: inline-block;
        background-color: #0284c7;
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 12px;
        margin-left: 8px;
    }
    
    /* Verbatim Review Box */
    .review-box {
        background-color: #1e293b;
        border-left: 4px solid #38bdf8;
        border-radius: 0 8px 8px 0;
        padding: 12px 16px;
        margin-bottom: 10px;
    }
    .review-text {
        font-size: 0.92rem;
        color: #f1f5f9;
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
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.72rem;
        font-weight: 600;
        background-color: #334155;
        color: #e2e8f0;
        margin-right: 6px;
    }
</style>
""", unsafe_allow_html=True)

# --- Load Data & Insights ---
@st.cache_data
def load_rq_insights():
    path = "backend/rq_insights.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data
def get_total_reviews_count():
    if os.path.exists("collected_data.json"):
        with open("collected_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return len(data)
    return 2226

insights_data = load_rq_insights()
total_reviews = get_total_reviews_count()

# --- Header ---
st.markdown(f"""
<div class="hero-header">
    <div class="hero-title">🛍️ Myntra Wishlist Conversion Discovery Engine</div>
    <div class="hero-subtitle">
        AI-synthesized strategic findings for all 10 core research questions generated directly from real customer reviews across Play Store, App Store, Twitter/X, YouTube, and Reddit.
    </div>
    <div class="stats-bar">
        <span class="stat-pill">📊 Total Customer Reviews: {total_reviews:,}</span>
        <span class="stat-pill">🎯 10 Core Research Questions</span>
        <span class="stat-pill">🌐 5 Data Platforms Analyzed</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- View Mode Selector ---
col_view, col_filter = st.columns([2, 1])
with col_view:
    view_mode = st.radio(
        "Display Mode:",
        ["Expandable Accordion View (All 10 Questions)", "Interactive Single Question Selector"],
        horizontal=True
    )

st.write("")

# --- Render Questions & Answers ---
if view_mode == "Interactive Single Question Selector":
    # Dropdown selector
    options = [f"RQ {k}: {v['title']} ({v['data_count']} reviews)" for k, v in insights_data.items()]
    selected_option = st.selectbox("Select a Research Question to inspect:", options, index=0)
    selected_key = selected_option.split(":")[0].replace("RQ", "").strip()
    
    q_data = insights_data.get(selected_key, {})
    if q_data:
        st.markdown("---")
        st.markdown(f"<span class='rq-badge'>RESEARCH QUESTION {q_data['number']}</span> <span class='data-pill'>📊 Backed by {q_data['data_count']} customer reviews ({q_data['data_ratio']}%)</span>", unsafe_allow_html=True)
        st.markdown(f"## **{q_data['title']}**")
        
        # AI Generated Answer
        st.markdown("### 💡 AI Answer (Generated from Customer Reviews)")
        st.markdown(q_data.get("ai_answer", ""))
        
        # Backing Customer Reviews
        st.markdown("---")
        reviews = q_data.get("backing_reviews", [])
        st.markdown(f"### 💬 Customer Reviews Backing This Answer ({len(reviews)} shown)")
        
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

else:
    # Accordion View for All 10 Questions
    for q_key in sorted(insights_data.keys(), key=lambda x: int(x)):
        q_data = insights_data[q_key]
        
        expander_title = f"RQ {q_data['number']}: {q_data['title']}  —  [{q_data['data_count']} backing reviews]"
        with st.expander(expander_title, expanded=(q_data['number'] == 1)):
            st.markdown(f"<span class='rq-badge'>QUESTION {q_data['number']}</span> <span class='data-pill'>📊 Backed by {q_data['data_count']} customer reviews ({q_data['data_ratio']}% of total dataset)</span>", unsafe_allow_html=True)
            
            # Answer Section
            st.markdown("#### 💡 AI Answer (Generated from Customer Reviews)")
            st.markdown(q_data.get("ai_answer", ""))
            
            # Backing Customer Reviews Section
            reviews = q_data.get("backing_reviews", [])
            st.markdown("---")
            st.markdown(f"#### 💬 Verbatim Customer Reviews Backing This Finding ({len(reviews)} reviews):")
            
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
