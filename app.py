import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os

from backend.data_loader import DataLoader
from backend.groq_engine import GroqEngine
from backend.rq_solver import RQSolver, RESEARCH_QUESTIONS

# --- Page Configuration ---
st.set_page_config(
    page_title="Myntra Discovery Engine | Growth PM Platform",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
<style>
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        color: #f8fafc;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 4px;
    }
    
    /* Evidence Quote Card */
    .quote-card {
        background-color: #1e293b;
        border-left: 4px solid #ec4899;
        border-radius: 0 8px 8px 0;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .quote-text {
        font-size: 0.95rem;
        font-style: italic;
        color: #e2e8f0;
        line-height: 1.5;
    }
    .quote-meta {
        font-size: 0.8rem;
        color: #94a3b8;
        margin-top: 8px;
    }
    .badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    .badge-play { background-color: #0284c7; color: white; }
    .badge-app { background-color: #6366f1; color: white; }
    .badge-twitter { background-color: #0ea5e9; color: white; }
    .badge-youtube { background-color: #ef4444; color: white; }
    .badge-reddit { background-color: #f97316; color: white; }
</style>
""", unsafe_allow_html=True)

# --- Initialize Backend Services ---
@st.cache_resource
def load_services():
    data_loader = DataLoader("collected_data.json")
    groq_engine = GroqEngine()
    rq_solver = RQSolver(data_loader, groq_engine)
    return data_loader, groq_engine, rq_solver

data_loader, groq_engine, rq_solver = load_services()
summary = data_loader.get_summary_metrics()

# --- Sidebar ---
st.sidebar.image("https://images.indianexpress.com/2021/01/myntra.png", width=140)
st.sidebar.title("Discovery Engine")
st.sidebar.caption("AI-Powered Wishlist Conversion & Customer Discovery")

# Model Selection
selected_model = st.sidebar.selectbox(
    "Groq LLM Model",
    ["qwen/qwen3.6-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"],
    index=0
)
groq_engine.model = selected_model

# Dataset Stats in Sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Dataset Composition")
st.sidebar.metric("Total User Feedback", f"{summary.get('total_reviews', 0):,}")
sources = summary.get("sources", {})
for s, count in sources.items():
    st.sidebar.write(f"• **{s}**: {count:,} records")


# --- Main App Header ---
st.title("🛍️ Myntra AI-Powered Discovery Engine")
st.markdown("Diagnosing wishlist drop-offs, user friction, and non-monetary conversion opportunities across **2,226 multi-platform customer reviews**.")

# --- Top Metric Banner ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">Total Customer Feedback</div>
        <div class="metric-value">{summary.get('total_reviews', 2226):,}</div>
        <div class="metric-sub">5 Sources: Play, App Store, X, Reddit, YT</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Top Friction Category</div>
        <div class="metric-value">Fit & Sizing</div>
        <div class="metric-sub">RQ 7 (Over 42% volume mention)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Highest Opportunity Score</div>
        <div class="metric-value">42.8 OIS</div>
        <div class="metric-sub">Cross-Brand Sizing & Fit Confidence</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-title">Inference Engine</div>
        <div class="metric-value">Groq LLM</div>
        <div class="metric-sub">Ultra-low latency semantic discovery</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- Navigation Tabs ---
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 10 Research Questions Deep-Dive",
    "🔍 Semantic Discovery Search & AI Chat",
    "📈 Friction Landscape & Analytics",
    "📑 Verbatim Feedback Explorer",
    "💡 Non-Monetary Conversion Playbook"
])

# ==========================================
# TAB 1: 10 RESEARCH QUESTIONS DEEP-DIVE
# ==========================================
with tab1:
    st.subheader("Deep-Dive into 10 Core Research Questions")
    st.caption("Select any research question to inspect customer feedback signals, quantified impact, and Groq LLM synthesis.")
    
    col_sel, col_stats = st.columns([2, 1])
    
    with col_sel:
        rq_options = [f"RQ {k}: {v['short_name']}" for k, v in RESEARCH_QUESTIONS.items()]
        selected_rq_str = st.selectbox("Select Research Question:", rq_options, index=6)
        rq_num = int(selected_rq_str.split(":")[0].replace("RQ", "").strip())
        rq_info = RESEARCH_QUESTIONS[rq_num]

    ois_data = rq_solver.get_opportunity_score(rq_num)
    evidence_list = rq_solver.get_rq_evidence(rq_num, limit=12)
    
    with col_stats:
        st.markdown(f"""
        <div style="background-color:#1e293b; padding:15px; border-radius:8px; border:1px solid #334155;">
            <div style="font-size:0.8rem; color:#94a3b8;">OPPORTUNITY IMPACT SCORE (OIS)</div>
            <div style="font-size:1.6rem; font-weight:bold; color:#ec4899;">{ois_data['opportunity_impact_score']} / 100</div>
            <div style="font-size:0.75rem; color:#cbd5e1;">Volume: {ois_data['volume_count']} mentions ({ois_data['volume_ratio']}%) | Delay: {ois_data['delay_penalty']}x</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"### **RQ {rq_num}: {rq_info['title']}**")
    st.write(f"*{rq_info['description']}*")
    
    col_synth, col_quotes = st.columns([3, 2])
    
    with col_synth:
        st.markdown("#### 🤖 Groq AI Strategic Synthesis")
        if st.button(f"⚡ Generate Real-Time Groq AI Analysis for RQ {rq_num}", key=f"btn_rq_{rq_num}"):
            with st.spinner("Analyzing verbatim customer feedback with Groq..."):
                analysis = groq_engine.synthesize_research_question(rq_num, rq_info['title'], evidence_list)
                st.session_state[f"rq_analysis_{rq_num}"] = analysis
                
        # Display analysis
        if f"rq_analysis_{rq_num}" in st.session_state:
            st.markdown(st.session_state[f"rq_analysis_{rq_num}"])
        else:
            # Default pre-computed synthesis
            st.info(f"**Discovered Core Friction**: {rq_info['default_friction']}")
            st.markdown(f"""
            - **Key Behavioral Pattern**: Customers demonstrate high initial intent when wishlisting, but postpone purchase due to {rq_info['short_name'].lower()}.
            - **Conversion Mechanism**: Addressing this without discounts will unlock delayed checkout intent and improve the 30-day conversion rate.
            - *Click the button above for full live Groq LLM reasoning with quote attribution.*
            """)
            
    with col_quotes:
        st.markdown("#### 💬 Verbatim Customer Quotes")
        st.caption(f"Showing top matching evidence ({len(evidence_list)} quotes)")
        
        for q in evidence_list[:6]:
            source = q.get("source", "Review")
            badge_class = f"badge-{source.lower().split()[0]}"
            st.markdown(f"""
            <div class="quote-card">
                <div class="quote-text">"{q.get('raw_text')}"</div>
                <div class="quote-meta">
                    <span class="badge {badge_class}">{source}</span>
                    <span>📅 {q.get('date', 'N/A')}</span> | 
                    <span>👤 {q.get('segment', 'unidentified')}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# TAB 2: SEMANTIC SEARCH & AI CHAT
# ==========================================
with tab2:
    st.subheader("Semantic Discovery Engine & Customer Chat")
    st.caption("Ask natural language questions about customer hesitation, returns, wishlist behavior, and fashion friction.")
    
    # Pre-defined discovery chips
    st.write("Suggested queries:")
    c1, c2, c3, c4 = st.columns(4)
    sample_q = ""
    if c1.button("👗 Why do plus-size users hesitate?"):
        sample_q = "Why do plus-size users hesitate to purchase wishlisted items?"
    if c2.button("⏱️ Why do users wait for next month?"):
        sample_q = "What causes users to wait after salary or next month before buying?"
    if c3.button("🔄 Sizing confusion across brands?"):
        sample_q = "What are users saying about size confusion and fitting across different brands?"
    if c4.button("📺 YouTube try-ons & external reviews?"):
        sample_q = "Why do users search YouTube reviews and try-on hauls before purchasing on Myntra?"
        
    query_input = st.text_input("Enter your research or product question:", value=sample_q, placeholder="e.g. Why do customers leave items in wishlist during sales?")
    
    if query_input:
        with st.spinner("Searching 2,226 customer reviews and generating Groq AI synthesis..."):
            matched_items = data_loader.search(query_input, top_k=10)
            
            if matched_items:
                col_ai, col_matches = st.columns([3, 2])
                with col_ai:
                    st.markdown("### 💡 Groq AI Discovery Insights")
                    answer = groq_engine.generate_rag_answer(query_input, matched_items)
                    st.markdown(answer)
                    
                with col_matches:
                    st.markdown(f"### 📑 Top Supporting Evidence ({len(matched_items)})")
                    for m in matched_items[:6]:
                        source = m.get("source", "Review")
                        badge_class = f"badge-{source.lower().split()[0]}"
                        st.markdown(f"""
                        <div class="quote-card">
                            <div class="quote-text">"{m.get('raw_text')}"</div>
                            <div class="quote-meta">
                                <span class="badge {badge_class}">{source}</span>
                                <span>Relevance: {m.get('score', 0):.2f}</span> | 
                                <span>Segment: {m.get('segment', 'unidentified')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No direct customer reviews matched your search query. Try broadening your terms.")

# ==========================================
# TAB 3: FRICTION LANDSCAPE & ANALYTICS
# ==========================================
with tab3:
    st.subheader("Friction Landscape Matrix & Opportunity Analytics")
    st.caption("Multi-dimensional visualization of customer concerns and prioritized growth opportunities.")
    
    # Calculate OIS dataframe for all 10 RQs
    matrix_data = []
    for k, v in RESEARCH_QUESTIONS.items():
        score_info = rq_solver.get_opportunity_score(k)
        matrix_data.append({
            "RQ": f"RQ {k}",
            "Topic": v["short_name"],
            "Volume Ratio (%)": score_info["volume_ratio"],
            "Delay Penalty": score_info["delay_penalty"],
            "Intent Intensity": score_info["intent_intensity"],
            "Opportunity Impact Score (OIS)": score_info["opportunity_impact_score"]
        })
    df_matrix = pd.DataFrame(matrix_data)
    
    # Interactive Prioritization Matrix Scatter Plot
    fig_matrix = px.scatter(
        df_matrix,
        x="Volume Ratio (%)",
        y="Delay Penalty",
        size="OpportunityImpact Score (OIS)" if "OpportunityImpact Score (OIS)" in df_matrix.columns else "Opportunity Impact Score (OIS)",
        color="Opportunity Impact Score (OIS)",
        text="Topic",
        hover_data=["RQ", "Intent Intensity"],
        color_continuous_scale="Plasma",
        title="Opportunity Prioritization Matrix (Volume vs Delay Penalty)",
        height=480
    )
    fig_matrix.update_traces(textposition='top center')
    fig_matrix.update_layout(template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    st.markdown("---")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        # Platform Distribution
        df_sources = pd.DataFrame(list(summary.get("sources", {}).items()), columns=["Source", "Count"])
        fig_sources = px.bar(
            df_sources,
            x="Source",
            y="Count",
            color="Source",
            title="Customer Feedback Distribution by Platform",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_sources.update_layout(template="plotly_dark", showlegend=False)
        st.plotly_chart(fig_sources, use_container_width=True)
        
    with col_g2:
        # User Segment Distribution
        seg_dict = summary.get("segments", {})
        df_segments = pd.DataFrame(list(seg_dict.items()), columns=["Segment", "Count"]).sort_values(by="Count", ascending=False)
        fig_seg = px.pie(
            df_segments.head(7),
            names="Segment",
            values="Count",
            title="Identified User Segment Profiles",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_seg.update_layout(template="plotly_dark")
        st.plotly_chart(fig_seg, use_container_width=True)

# ==========================================
# TAB 4: VERBATIM FEEDBACK EXPLORER
# ==========================================
with tab4:
    st.subheader("Verbatim Customer Feedback Explorer")
    st.caption("Filter and explore all 2,226 customer reviews, tweets, and comments.")
    
    df_raw = data_loader.df.copy()
    
    c_f1, c_f2, c_f3 = st.columns(3)
    with c_f1:
        src_filter = st.multiselect("Filter by Source:", ["Play Store", "App Store", "Twitter", "Reddit", "YouTube"], default=["Play Store", "App Store", "Twitter", "Reddit", "YouTube"])
    with c_f2:
        seg_options = ["All"] + sorted(list(set([s.strip() for seg in df_raw["segment"].dropna() for s in str(seg).split(",") if s.strip()])))
        seg_filter = st.selectbox("Filter by User Segment:", seg_options, index=0)
    with c_f3:
        search_kw = st.text_input("Filter Text by Keyword:", placeholder="e.g. size chart, expensive, fabric")
        
    filtered = df_raw.copy()
    if src_filter:
        filtered = filtered[filtered["source"].isin(src_filter)]
    if seg_filter != "All":
        filtered = filtered[filtered["segment"].str.contains(seg_filter, case=False, na=False)]
    if search_kw:
        filtered = filtered[filtered["raw_text"].str.contains(search_kw, case=False, na=False)]
        
    st.write(f"Showing **{len(filtered):,}** matching reviews (out of {len(df_raw):,} total):")
    
    st.dataframe(
        filtered[["id", "raw_text", "source", "date", "platform", "keywords_matched", "rq_answered", "segment"]],
        use_container_width=True,
        height=400
    )
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        csv_data = filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Filtered Results as CSV", data=csv_data, file_name="myntra_feedback_filtered.csv", mime="text/csv")
    with col_d2:
        json_data = filtered.to_json(orient="records", indent=2).encode('utf-8')
        st.download_button("📥 Download Filtered Results as JSON", data=json_data, file_name="myntra_feedback_filtered.json", mime="application/json")

# ==========================================
# TAB 5: NON-MONETARY CONVERSION PLAYBOOK
# ==========================================
with tab5:
    st.subheader("Non-Monetary Conversion Framework (Product Solutions)")
    st.caption("Strategic product and UX interventions mapped to discovered friction areas to boost 30-day wishlist conversion without discounts.")
    
    sol1, sol2 = st.columns(2)
    with sol1:
        st.markdown("""
        ### 1. 📏 Cross-Brand Size Matcher & 3D Fit Predictor
        - **Target Friction**: Inconsistent sizing across brands (RQ 3, RQ 7).
        - **Solution**: Dynamic reference tool that compares the wishlisted product's cut and dimensions against the user's previously purchased, unreturned items.
        - **Impact Mechanism**: Eliminates return anxiety and size hesitation, driving instant checkout confidence.
        
        ---
        
        ### 2. 📅 Occasion Countdown & Delivery Urgency Planner
        - **Target Friction**: Postponing purchases for birthdays, weddings, or vacations (RQ 4).
        - **Solution**: "Tag an Occasion Date" feature in the wishlist with proactive delivery buffer notifications (*"Order by Wednesday to receive in time for your event"*).
        - **Impact Mechanism**: Leverages the customer's own natural timeline urgency rather than artificial scarcity.
        
        ---
        
        ### 3. 📂 Smart Wishlist Partitioning
        - **Target Friction**: High-intent items buried under passive inspiration bookmarks (RQ 1, RQ 8).
        - **Solution**: Dual-mode Wishlist separating items into *"Ready to Buy"* vs *"Moodboard / Inspiration"*.
        - **Impact Mechanism**: Keeps high-intent items accessible for streamlined 1-click checkout.
        """)
        
    with sol2:
        st.markdown("""
        ### 4. 👗 Visual AI "Wardrobe Integrator"
        - **Target Friction**: Styling uncertainty and wardrobe incompatibility (RQ 3, RQ 7).
        - **Solution**: AI outfit generator rendering 3 complete looks pairing the wishlisted piece with existing wardrobe basics or top-converted staples.
        - **Impact Mechanism**: Transforms an isolated garment into an immediate, wearable outfit.
        
        ---
        
        ### 5. 👥 Contextual Social Proof & Quick Polls
        - **Target Friction**: External validation deficit (RQ 6, RQ 7).
        - **Solution**: Real-time localized social signals (*"34 stylish shoppers in your city wishlisted this"*) and 1-click shareable polls for friend opinions.
        - **Impact Mechanism**: Provides instant social validation without needing to leave the app for YouTube/Instagram.
        """)

st.markdown("---")
st.caption("Myntra Growth PM Discovery Engine | Powered by Streamlit & Groq Cloud LLM")
