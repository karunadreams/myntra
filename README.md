# 🛍️ Myntra AI-Powered Discovery Engine & Growth PM Platform

An AI-powered customer discovery and analytics system designed for Growth Product Managers to diagnose why wishlisted fashion products are not purchased, quantify core friction points, and unlock 30-day wishlist conversion through **non-monetary product interventions**.

Powered by **Groq Cloud LLM** (`qwen/qwen3.6-27b` / `openai/gpt-oss-120b`), a **2,226-item multi-platform dataset**, and an interactive **Streamlit Web Application**.

---

## 🚀 Key Features

1. **📊 10 Core Research Questions Deep-Dive**:
   - Automated semantic reasoning and strategic PM synthesis for all 10 foundational research questions.
   - Dynamic **Opportunity Impact Score (OIS)** calculation ($OIS = \text{Volume} \times \text{Delay Penalty} \times \text{Intent Intensity}$).
   - Direct attribution to verbatim customer evidence quotes with source and segment tags.

2. **🔍 Semantic Discovery Search & AI Chat**:
   - Natural language search over the 2,226 customer reviews using TF-IDF vector embeddings and cosine similarity.
   - Ultra-fast Groq LLM RAG engine synthesizing root causes, affected personas, and UX recommendations.

3. **📈 Friction Landscape & Opportunity Matrix**:
   - Interactive Plotly scatter plot visualizing customer friction areas (Volume vs Delay Penalty).
   - Platform distributions (Play Store, App Store, Twitter/X, YouTube, Reddit) and user segment breakdowns (`plus size`, `budget shopper`, `student`, `gift buyer`).

4. **📑 Verbatim Feedback Explorer**:
   - Multi-dimensional filtering by source, segment, and keyword.
   - Instant export to CSV and JSON formats.

5. **💡 Non-Monetary Conversion Playbook**:
   - Actionable product solutions (Cross-Brand Size Matcher, Occasion Countdown Planner, Smart Wishlist Partitioning, Visual Wardrobe Integrator).

---

## 📊 Dataset Summary

| Source | Raw Scraped | Verified Qualifying Rows | Platform Type |
| :--- | :--- | :--- | :--- |
| **Google Play Store** | 1,000 | **1,000** | Android App Reviews |
| **Apple App Store** | 570 | **570** | iOS App Reviews |
| **Twitter / X** | 1,036 | **531** | Public Tweets & Discussions |
| **YouTube** | 653 | **64** | Video Try-On & Haul Comments |
| **Reddit** | 493 | **61** | Fashion & E-commerce Subreddits |
| **Total Master Dataset** | **3,752** | **2,226** | Stored in `collected_data.json` & `collected_data.md` |

---

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/karunadreams/myntra.git
cd myntra
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Credentials
Create a `.env` file (refer to `.env.example`):
```env
groq_api=your_groq_api_key_here
APIFY_API_TOKEN=your_apify_token_here
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

---

## 📂 Project Structure

```text
myntra/
├── .env.example                 # Environment configuration template
├── .gitignore                   # Git ignore rules (secrets protected)
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
├── app.py                       # Main Streamlit Application
├── architecture.md              # Full System Architecture Plan
├── prob.md                      # Problem Statement & 10 Research Questions
├── collected_data.json          # Master 2,226 verified feedback dataset
├── collected_data.md            # Markdown table representation
├── combined_raw_data.json       # Master 2,182 unedited raw payloads
├── collect_apify_data.py        # Multi-platform Apify scraper
├── backend/                     # Decoupled Backend Engine
│   ├── __init__.py
│   ├── data_loader.py           # Dataset caching & TF-IDF search index
│   ├── groq_engine.py           # Groq LLM client & RAG pipeline
│   └── rq_solver.py             # 10 Research Questions solver & OIS engine
└── *.json                       # Platform raw and filtered archives
```

---

## 🌐 Deploy to Streamlit Community Cloud

1. Fork or push this repository to GitHub.
2. Log in to [share.streamlit.io](https://share.streamlit.io/).
3. Select your repository and `app.py` as the main file path.
4. Under **Advanced Settings > Secrets**, add:
   ```toml
   groq_api = "gsk_..."
   ```
5. Click **Deploy**!
